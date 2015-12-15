__author__ = 'Bassel Khatib & Michael Hundt'


from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener


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

    stream = Stream(auth, l)

    # take the 'random' sample data, which Twitter provide
    stream.sample()

    # Filter for keywords
    #stream.filter(track=['Love', 'air'])

    # Filter for location
    #stream.filter(locations= (-74,40,-73,41))  # New York, WGS 84 projection
