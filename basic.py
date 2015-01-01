"""
Collecting Time series data
"""
import os
import twitter, json
from functools import partial
import sys, datetime, time
import matplotlib.pyplot as plt
import pylab
from prettytable import PrettyTable as pt

tt = pt(["Bin", "ID", "Text"])
tt.align["Bin"]
tt.padding_with = 1

pp = partial(json.dumps, indent = 1)
q = '' #query phrase
start_time = str(datetime.datetime.now())[:-7]
path_to_file = q + "/" + start_time


ttf = open("tweet-table" + " " + q +".txt", 'w')


f.write(start_time+"/"+start_time + "\n")

def oauth_login():
	CONSUMER_KEY = ''
	CONSUMER_SECRET =''
	OAUTH_TOKEN = '-'
	OAUTH_TOKEN_SECRET = ''

	auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
	twitter_api = twitter.Twitter(auth=auth)
	return twitter_api

""" ---- DO THINGS ---- """
print >> sys.stderr, 'Filtering the public timeline for track="%s"' % (q,)
twitter_api = oauth_login()
print twitter_api
twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)
stream = twitter_stream.statuses.filter(track=q)

#CHANGE NEEDED VARIABLES HERE
c = 0
tc = 0
alpha = 0.3
s_s = []
s_x = []
s_times = {}
s_raw = {}
gr = []

abs_tc = 0

sfreq = [0]
freq = []

#change these two values to choose how long the program shall run, and also how large each bin will be

lim = 3600*24*7 # in seconds
timeframe = 60 * 1 #in seconds

def find_smooth(c, depth = 0): #not called when c is 0
	global sfreq
	global freq
	global alpha
	if c == 0:
		return sfreq[0]
	elif not c == 0 and depth > 500:
		return sfreq[c-501]
	else:
		return alpha * freq[c-1] + (1-alpha) * find_smooth(c-1, depth + 1)

g = open("raw-tweets.txt", 'w')
z = open("ema-tweet-freq.txt", 'w')
rawh = open("raw_freq.txt", 'w')
dt_i = int(time.time())
dt_t = str(datetime.datetime.now())[:-7]
for tweet in stream:

	abs_tc += 1
	#print "tweet"
	dt = int(time.time()) - dt_i #current time
	#print "current time: " + str(dt) + "\n"
	try:
		g.write(str(dt) + " " + tweet['text'].encode('ascii', 'ignore') + "\n")
	except:
		g.write("UNSUPPORTED TEXT \n")
	
	try: 
		zz = s_times[(dt//timeframe)]
		zz = s_times[(dt//timeframe)]
	except KeyError:
		s_times[(dt//timeframe)] = []
		s_raw[(dt//timeframe)] = 0
	try:
		s_times[(dt//timeframe)].append(tweet['text'].encode('ascii', 'ignore'))
	except:
		s_times[(dt//timeframe)].append("nope")
	s_raw[(dt//timeframe)] += 1
	try:
		tt.add_row([str(dt//timeframe), tweet['id'], tweet['text'].encode('ascii', 'ignore')])
	except KeyError:
		pass
	try:
		dt == prev #is this tweet the same bin as the previous one?
	except NameError: #only happens for 1st tweet

		prev = dt
		continue
	if dt == prev: #if same bin
	#	print "dt is " + str(dt)
	#	print "prev is " + str(prev) + "\n"
		tc += 1 #increase number in bin

	else: #if not same bin		
		c += 1
		tc = 0
		prev = dt		

	if dt >= lim:
		ttf.write(str(tt))
		print pp(s_raw)
		for a in s_raw:
			rawh.write(str(s_raw[a]) + "\n")
		_maxa = 0
		

		#print "smoothed : " + str(s_s)
		for a in xrange(_maxa):
			if a not in [b for b in iter(s_raw)]:
				freq.append(0)
			else:
				freq.append(s_raw[a])
		print pp(freq)
		print "length of freq is: " + str(len(freq)) + "\n"
		for a in xrange(len(freq)):
			if a == 0:
				sfreq.append(0)
			else:
				print "smoothing " + str(freq[a])
				sfreq.append(find_smooth(a))
		z.write(pp(sfreq))
		print pp(sfreq)
		print "processed " + str(abs_tc) + " tweets"
		plt.plot([a for a in s_times], [len(s_times[a]) for a in s_times], '-r')
		plt.plot([a for a in xrange(len(sfreq))], [a for a in sfreq], '-b')
		plt.plot([a for a in xrange(len(sfreq))], [a for a in sfreq], '+')
		plt.title(q + ' ' + dt_t)
		plt.xlabel("Time frame of " + str(timeframe) + " second(s)")
		plt.ylabel("Bin size")
		plt.draw()
		fig1 = plt.gcf()
		fig1.savefig("plot" + ".svg")

		break

