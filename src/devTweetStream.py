import tweetstream

#words = ['bugger','london']
user = 'RedSquirrelDev'
password = 'RedSquirrelDev00!'


locations = ["-122.75,36.8", "-121.75,37.8", "-0.15,51.50", "-0.10,51.55"]

stream = tweetstream.FilterStream(user, password, locations=locations)

for tweet in stream:
    print tweet
    print dir(tweet)