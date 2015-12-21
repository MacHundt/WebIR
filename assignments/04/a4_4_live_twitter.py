import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

__author__ = 'Bassel Khatib & Michael Hundt'




consumer_key = "pVCg0oEa9s6wk6R8RpgYOpuok"
consumer_secret = "UfbNG37J8BxYyyykiw00AO3JLCK52006hIbf03J1WHJtFOxdOu"

access_token = "3341183098-GExENkUKQNOSRolnb0g1wlEijy5kjqXRciCsOMs"
access_token_secret = "qNdwScwMI1JIWqh8xmTshL9m4hieVMbcRRGfYEKxsZTS9"


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':



    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Construct the API instance
    api = tweepy.API(auth)

    # followers and friends ?
    #friends = api.lookup_friendships(api)
    # for user in tweepy.Cursor(api.followers, screen_name="twitter").items():
    #     if user.geo_enabled:
    #         print(user.screen_name + " - "+ str(user.followers_count) + " - ")

    # for follower in tweepy.Cursor(api.followers).items():
    #     follower.follow()

    # tweets that I follow
    # public_tweets = api.home_timeline()
    # for tweet in public_tweets:
    #     print(tweet.text)

    # Open Stream
    stream = Stream(auth, l)

    # take the 'random' english sample data, which Twitter provide
    #stream.sample(languages=["en"])

    # Filter for keywords
    #stream.filter(track=['Love', 'air'])

    # Filter for location in WGS 84 projection
    #stream.filter(locations= (-74,40,-73,41))      # New York
    stream.filter(locations= (-180,-90,180,90), languages=["en"])     # whole World, english
