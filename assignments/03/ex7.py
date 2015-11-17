# -*- coding: utf-8 -*-

# Ex 7: Logging


import logging


def init_log(file_n="execution.log",
             file_m="a",
             lvl=logging.DEBUG,
             fmt="%(asctime)s %(levelname)s: %(message)s.",
             d_fmt="%d.%m.%Y %H:%M:%S"):

    logging.basicConfig(filename=file_n,
                        filemode=file_m,
                        level=lvl,
                        format=fmt,
                        datefmt=d_fmt)


def shutdown_log():
    logging.shutdown()


def write_header():
    logging.info("Start logging")


def write_footer():
    logging.info("End logging")


def main():
    init_log(file_n="log.txt")
    logging.info("<< Starting Log >>")
    try:
        a = 5
        a.append(6)
    except Exception as e:
        logging.error("What are you doing?!: %s!" % e)
    logging.info("<< End Log >>")
    shutdown_log()

if __name__ == '__main__':
    main()
