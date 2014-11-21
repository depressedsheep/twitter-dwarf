"""
Collecting Time series data
"""
import os
import twitter, json
from functools import partial
import sys, datetime, time
import pymongo
import matplotlib.pyplot as plt
import pylab
pp = partial(json.dumps, indent = 1)
q = 'Obama'
start_time = str(datetime.datetime.now())[:-7]
path_to_file = q + "/" + start_time
os.makedirs(path_to_file)
f = open(path_to_file +"/time-stream" + " " + q + " " + start_time, 'w')



f.write(start_time+"/"+start_time + "\n")

def oauth_login():
	CONSUMER_KEY = '7F4rMIJZ89bKofuTqqTf0MI7p'
	CONSUMER_SECRET ='M0GPMQALGJ576RZJSHEmri5QsgyogqBqy7HMqQIksfa4SUIcIy'
	OAUTH_TOKEN = '227639950-pVW3ukNAO37bE6fuLJeSajmWQTD6iKx1UQFUSpOg'
	OAUTH_TOKEN_SECRET = 'UqFMvQWsi4afXrVJr7ExRlKeaMDMMPtzC1BHT0yafQkdg'

	auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
	twitter_api = twitter.Twitter(auth=auth)
	return twitter_api
"""
def twitter_search(twitter_api, q, max_results = 200, **kw):
	search_results = twitter_api.search.tweets(q=q, count = 100, **kw)
	statuses = search_results['statuses']
	max_results = min(1000, max_results)
	for _ in range(10):
		try:
			next_results = search_results['search_metadata']['next_results']
		except KeyError, e:
			break
		kwargs = dict([kv.split('=') for kv in next_results[1:].split("&")])
		search_results = twitter_api.search.tweets(**kwargs)
		statuses += search_results['statuses']
		if len(statuses) > max_results:
			break
	return statuses

def get_time_series_data(api_func, mongo_db_name, mongo_db_coll, secs_per_interval=60, max_intervals = 15, **mongo_conn_kw):
	interval = 0
	while True:
		now = str(int(time.time() * 1000))
		ids = save_to_mongo(api_func, mongo_db_name, mongo_db_coll + "-" + now)
		print >> sys.stderr, "Write {0} statuses".format(len(ids))
		print >> sys.stderr, "Zzz..."
		print >> sys.stderr.flush()
		time.sleep(secs_per_interval) # seconds
		interval += 1
		if interval >= 15:
			break
def save_to_mongo(data,mongo_db, mongo_db_coll, **mongo_conn_kw):
	client = pymongo.MongoClient(**mongo_conn_kw)
	db = client[mongo_db]
	coll = db[mongo_db_coll]
	return coll.insert(data)	
def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False, criteria=None, projection=None, **mongo_conn_kw):
	client = pymongo.MongoClient(**mongo_conn_kw)
	db = client[mongo_db]
	coll = db[mongo_db_coll]
	if criteria is None:
		criteria = {}
	if projection is None:
		cursor = coll.find(criteria)
	else:
		cursor = coll.find(critiera,projection)
	if return_cursor:
		return cursor
	else:
		print [item for item in cursor]
		"""

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
s_times = []
gr = []
lim = 100
def find_smooth(c, depth = 0): #not called when c is 0
	global s_s
	global s_x
	global alpha
	if c == 0:
		return s_s[0]
	elif not c == 0 and depth > 500:
		return s_s[c-501]
	else:
		return alpha * s_x[c-1] + (1-alpha) * find_smooth(c-1, depth + 1)

g = open(path_to_file + "/tweets.txt", 'w')
for tweet in stream:
	dt = int(time.time()) #current time
	try:
		g.write(str(dt) + " -- " + tweet['text'].encode('ascii', 'ignore') + "\n")
	except UnicodeEncodeError:
		g.write("UNSUPPORTED TEXT \n")
		

	try:
		dt == prev #is this tweet the same bin as the previous one?
	except NameError: #only happens for 1st tweet
		#print "omggg"
		prev = dt
		continue
	#print "dt is " + str(dt)
	#print "prev is " + str(prev)
	if dt == prev: #if same bin
		tc += 1 #increase number in bin
		#print "tc is " + str(tc)
	else: #if not same bin
		f.write(str(prev) + " " + str(tc) +"\n") #write the prev bin to file
		#print c
		#print s_s
		#print s_x
		if not c == 0:
			s_t = find_smooth(c)
			s_s.append(s_t)
			s_x.append(tc)
			s_times.append(prev)

		else:
			s_x.append(tc)
			s_s.append(tc)
			s_times.append(prev)
		if c > 9:
			try:
				gr.append((s_t - s_s[c - 10])/s_s[c-10])
				if gr[-1] > 15:
					print "something's happening"
			except ZeroDivisionError:
				gr.append(None)
		else:
			gr.append(None)
		#p_d.append([dt, tc])
		c += 1
		tc = 0
		prev = dt
	

	load_text = "[" + int(c/float(lim) * 100 - 1) * "=" + ">" + (100 - int(c/float(lim) * 100)) * " " + "] (" + str(c) + " out of " + str(lim) + ")"
	try:
		if not load_text == prev_load_text:
			print load_text
	except NameError:
		pass
		
	if c == lim:
		#print "smoothed : " + str(s_s)
		plt.plot(s_times, s_s, "-b")
		plt.plot(s_times, gr, "-g")
		pylab.ylim([0,100])
		#plt.plot(s_times, s_x, "-r")
		fig1 = plt.gcf()
		plt.show()
		plt.draw()
		fig1.savefig(path_to_file+"/"+q + "-" + start_time + ".svg")

		plt.plot(s_times, s_x, "-r")
		pylab.ylim([0,100])
		fig2 = plt.gcf()
		plt.show()
		plt.draw()
		fig2.savefig(path_to_file+"/"+q + "-" + start_time+"-RAW.svg")

		#plt.plot(s_times, gr, "-g")
		#pylab.ylim([0,100])
		#fig3 = plt.gcf()
		#plt.show()
		#plt.draw()
		#fig3.savefig(start_time+"/"+q + "-"+start_time+"-growth.svg")

		break
		#save_to_mongo(tweet, "time-series", str(int(time.time())))
	
	prev_load_text = load_text
