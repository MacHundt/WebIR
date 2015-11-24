"""
A script for crawling of Wikipedia pages. It takes advantage of Python's Coroutines (like fibers, green threads)
to asynchronously make HTTP requests. It uses a configurable number of tasks to make requests, which are all
scheduled cooperatively; no synchronization required, as only one thread is used. The implementation draws heavily from
the available documentation on Python Coroutines[0]. The crawler is quite fast and I learned a lot about concurrency
in Python :).

Running on my MacBookPro 4-Core laptop: 147.333 urls/sec/task. The sweet spot of #tasks seems
to be at around 16 tasks. Above 20 tasks the performance gets worse, below 10 tasks the performance is not optimal.
"""
import asyncio
import logging
import re
import urllib.parse
from asyncio import Queue
from collections import namedtuple
# pip3 install aiohttp
import aiohttp
from time import time, ctime
# pip3 install beautifulsoup4
from bs4 import BeautifulSoup
from sys import stderr
from operator import attrgetter
from csv import writer


# The regex filters urls that we do not want to access.
# For tests see: http://regexr.com/3c5jk
# I added wiki to exclude pages with w/index.php?title=TITLE_OF_PAGE because they point to the same page
# without redirecting, so they get crawled twice!
# Also I removed some overview and data pages so that we limit ourselves to the more page-like pages, so that we do
# not get all these year-overview pages that spam our queue.
INTERNAL_LINK_RE = r'^\/(?:wiki\/)(?!(Datei:|Kategorie:|Wikipedia:)).*'

LOGGER = logging.getLogger(__name__)

def is_redirect(code):
    return code in (300,301,302,303,307)

ResponseInfo = namedtuple('ResponseInfo',
                          ['url', 'level', 'redir_url','status', 'exception','num_urls', 'num_new_urls'])


class Crawler:
    """
    An asynchronous crawler for Wikipedia pages.
    """
    def __init__(self, root,
                 max_level=2,
                 max_redirect=10,
                 max_tries=4,
                 max_tasks=16):
        self.loop = asyncio.get_event_loop()
        self.root = root
        self.max_redirect = max_redirect
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.max_level = max_level
        self.q = Queue(loop=self.loop)
        self.seen_urls = set()
        # accessed urls
        self.done = []
        self.session = aiohttp.ClientSession(loop=self.loop)

        host, port = urllib.parse.splitport(urllib.parse.urlparse(root).netloc)
        self.root_domain = host

        self.add_url(root, 0)

        self.t0 = time()
        self.t1 = None

    def close(self):
        self.session.close()

    def url_allowed(self, url):
        """
        Limit the crawling to allowed urls.
        :param url: url to test
        :return: true if the url is allowed to be crawled, false otherwise
        """
        host, port = urllib.parse.splitport(urllib.parse.urlparse(url).netloc)
        return host == self.root_domain

    def add_url(self, url, level, max_redirect=None):
        """
        Add the given url to the seen urls and the queue.
        :param url: url to add
        :param level: level of the url
        :param max_redirect: number of redirects for the url left
        :return:
        """
        if max_redirect is None:
            max_redirect = self.max_redirect
        self.seen_urls.add(url)
        self.q.put_nowait((url, level, max_redirect))

    def record_response(self, response_info):
        """
        Records the response at the appropriate level.
        :param response_info: info about the response
        :return:
        """
        self.done.append(response_info)

    @asyncio.coroutine
    def parse_links(self, response, level):
        """
        Parse links on a page represented by the given response. The level in the crawling-hierarchy is indicated.
        :param response: page to parse links on
        :param level: level of the given page in the craweling-hierarchy
        :return: information about the response and the links found
        """
        links = set()
        body = yield from response.read()

        if response.status == 200:
            text = yield from response.text()
            # explicit specification of the parser is recommended by bs4
            # optimally, we could check for the appropriate content-type and choose the parser based on that
            # e.g. xml.parser for content-type application/xml
            bs = BeautifulSoup(text, 'html.parser')
            anchors = bs.findAll('a', href=re.compile(INTERNAL_LINK_RE))

            if anchors:
                LOGGER.info('Got %r distinct urls from %r', len(anchors), response.url)

            for a in anchors:
                url = a.get('href')
                # the next two statements clean up the url we want to add
                joined = urllib.parse.urljoin(response.url, url)
                u, fragment = urllib.parse.urldefrag(joined)
                links.add(u)

        resp = ResponseInfo(url=response.url,
                            level=level,
                            redir_url=None,
                            status=response.status,
                            exception=None,
                            num_urls=len(links),
                            num_new_urls=len(links - self.seen_urls)
                            )

        return resp, links

    def handle_redirect(self, response, url, level, max_redirect):
        """
        Handle redirects.
        :param response: response
        :param url: url that got redirected
        :param level: level in the hierarchy we are at
        :param max_redirect: number of allowed redirects left
        :return:
        """
        location = response.headers['location']
        redir_url = urllib.parse.urljoin(url, location)
        # we record a response for the redirect
        self.record_response(
            ResponseInfo(url=url, level=level, redir_url=redir_url, status=response.status, exception=None, num_urls=0,
                         num_new_urls=0)
        )
        if redir_url in self.seen_urls:
            # do not follow seen urls
            return
        # do not follow too many redirects
        if max_redirect > 0:
            LOGGER.info('Redirect to %r from %r', redir_url, url)
            # On redirects we leave the level the same
            self.add_url(redir_url, level, max_redirect - 1)
        else:
            LOGGER.error('Redirect limit reached for %r from %r', redir_url, url)

    @asyncio.coroutine
    def fetch(self, url : str, level : int, max_redirect : int):
        """
        Fetch the given url at the given level.
        :param url: url to fetch
        :param level: the urls level in the hierarchy
        :param max_redirect: maximum number of redirects
        :return:
        """
        LOGGER.debug('Fetching at %r the url %r', level, url)
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                # wait 2 seconds for response...
                response = yield from asyncio.wait_for(self.session.get(url, allow_redirects=False), timeout=2)
                if tries > 1:
                    LOGGER.info('Try %r for %r success.', tries, url)
                break

            except (asyncio.TimeoutError, TimeoutError) as e:
                LOGGER.error('Requeueing after timeout: %r', url)
                # When we get a timeout, we do not want to try the url again now, but we requeue it
                self.q.put_nowait((url, level, max_redirect))
                # Another possibility would be a separate worker that sleeps (and blocks execution) for an adaptive
                # time, until requests are answered again
                exception = e
            except aiohttp.ClientError as e:
                LOGGER.info('Try #%r for %r raised %r', tries, url, e)
                exception = e
            tries += 1
        else:
            LOGGER.error('%r failed after %r tries', url, self.max_tries)
            self.record_response(ResponseInfo(url=url, level=level, redir_url=None, status=None, exception=exception,
                                              num_urls=0, num_new_urls=0))
            return

        try:
            if is_redirect(response):
                self.handle_redirect(response, url, level, max_redirect)
            else:
                resp, links = yield from self.parse_links(response, level)
                self.record_response(resp)
                # enqueue only if we are not on the last level already and record all the urls instead
                # this means that we do not have to use a worker for every url on the last level
                child_level = level + 1
                for link in links.difference(self.seen_urls):
                    if child_level == self.max_level:
                        LOGGER.debug('Only storing at %r url %r', child_level, link)
                        # we only want to enqueue links that we actually have to fetch
                        self.record_response(ResponseInfo(url=link, level=child_level, redir_url=None, status=None,
                                                          exception=None, num_urls=None, num_new_urls=None))
                    else:
                        self.q.put_nowait((link, child_level, self.max_redirect))
                self.seen_urls.update(links)
        finally:
            yield from response.release()

    @asyncio.coroutine
    def work(self):
        try:
            while True:
                url, level, max_redirect = yield from self.q.get()
                assert url in self.seen_urls
                yield from self.fetch(url, level, max_redirect)
                self.q.task_done()
        except asyncio.CancelledError:
            # swallow task cancelled errors
            pass

    @asyncio.coroutine
    def crawl(self):
        # wrap the coroutine in a task and execute it on the configured loop
        workers = [asyncio.Task(self.work(), loop=self.loop) for _ in range(self.max_tasks)]
        self.t0 = time()
        yield from self.q.join()
        self.t1 = time()
        # we need to cancel our workers when the queue is empty
        for w in workers:
            w.cancel()


def report(crawler : Crawler, csv_file_name=None):
    """
    Report crawler results.
    :param crawler: crawler to report on
    :param csv_file_name: name of csv file to write urls into
    :return:
    """
    t1 = crawler.t1 or time()
    dt = t1 - crawler.t0
    num = len(crawler.done)
    if dt and crawler.max_tasks:
        speed = (num) / dt / crawler.max_tasks
    else:
        speed = 0
    print('>>> Report <<<')
    try:
        show = list(crawler.done)
        show.sort(key=attrgetter('level','url'))

        if csv_file_name:
            csv_file = open(csv_file_name, 'w', newline='')
            wr = writer(csv_file, delimiter=';')

            for rec in show:
                if wr:
                    wr.writerow([rec.level, rec.url])
                else:
                    if rec.exception:
                        print(rec.url, 'error', rec.exception)
                    elif rec.redir_url:
                        print(rec.url, rec.status, 'redirect', rec.redir_url)
                    else:
                        print(rec.url, rec.level, rec.status)
            if csv_file:
                csv_file .close()
    except KeyboardInterrupt:
        print('Interrupted.')
    print('Date:', ctime(), 'local time')
    print('Finished', num, 'urls in %.3f secs' % dt, '(max_tasks=%d)' % crawler.max_tasks,
          '(%.3f urls/sec/task)' % speed)
    print('Todo:', crawler.q.qsize())
    print('Done:', num)

def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(enabled=False)

    # Configure the crawler
    level = 2 # level at which we want to stop
    tasks = 16 # number of tasks we use for crawling
    root = 'https://de.wikipedia.org/wiki/Wikipedia:Hauptseite'

    logging.basicConfig(level=logging.INFO, filename='crawler-level-{0}.log'.format(level))
    crawler = Crawler(root, max_level=level, max_tasks=tasks)

    # Run the crawler in the asyncio's loop and clean up afterwards
    try:
        loop.run_until_complete(crawler.crawl())
    except KeyboardInterrupt:
        stderr.flush()
        print('Interrupted.')
    finally:
        report(crawler, csv_file_name='level-{0}-urls.csv'.format(level))
        crawler.close()

        # Cleanup aiohttp resources
        loop.stop()
        loop.run_forever()
        loop.close()
        logging.shutdown()

if __name__ == '__main__':
    main()


# Literature[0]:
# https://docs.python.org/3/library/asyncio-task.html
# http://aiohttp.readthedocs.org/en/stable/
# http://aosabook.org/en/500L/a-web-crawler-with-asyncio-coroutines.html
