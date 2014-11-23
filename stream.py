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
from config import ck, cs, ot, ots
from prettytable import PrettyTable
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import math
tokenizer = RegexpTokenizer(r'\w+')

pp = partial(json.dumps, indent = 1)
q = 'Obama'
start_time = str(datetime.datetime.now())[:-7]
path_to_file = q + "/" + start_time
os.makedirs(path_to_file)
f = open(path_to_file +"/time-stream" + " " + q + " " + start_time, 'w')

f.write(start_time+"/"+start_time + "\n")

table_raw = PrettyTable(["Time", "ID", "Text"])
table_entities = PrettyTable(["Time", "ID", "Mentions", "Hashtags"])
table_nontrivial = PrettyTable(["Time",  "ID", "Text"])

table_raw.align["Time"] = "l"
table_raw.padding_width = 1
table_entities.align["Time"] = "l"
table_entities.padding_width = 1
table_nontrivial.align["Time"] = "l"
table_nontrivial.padding_width = 1
def r(x,n):
	return round(x, int(n - math.ceil(math.log10(abs(x)))))

def oauth_login():
	CONSUMER_KEY = ck
	CONSUMER_SECRET = cs
	OAUTH_TOKEN = ot
	OAUTH_TOKEN_SECRET = ots

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
s_times = []
gr = []
lim = 10

t_ha = {}
t_me = {}
vocab = {}
t_x = 0 #number of tweets
t_vectors = {}

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

g = open(path_to_file + "/tweets-RAW.txt", 'w')
h = open(path_to_file + "/tweet-entities.txt",'w')
nt = open(path_to_file + "/tweets-nontrivial.txt", 'w')
dt_i = int(time.time())
for tweet in stream:
	t_x += 1
	#DEF TEMP VARIABLES
	_denm = {} #temporary : _ entity dictionary for mentions
	_denh = {} #temporary : _ entity dictionary for hashtags
	temp_indices = [] #removing user mentions
	temp_vocab = {} #tweet by tweet basis
	temp_vector = {}  #tweet by tweet basis

	if c == lim:
		#print s_times
		#print "smoothed : " + str(s_s)
		#print pp(t_ha)
		#print pp(vocab)
		g.write(str(table_raw))
		nt.write(str(table_nontrivial))
		plt.plot(s_times, s_s, "-b")
	#	plt.plot(s_times, gr, "-g")
		pylab.ylim([0,100])
		#plt.plot(s_times, s_x, "-r")
		fig1 = plt.gcf()
	#	plt.show()
		plt.draw()
		fig1.savefig(path_to_file+"/"+q + "-" + start_time + ".svg")

		plt.plot(s_times, s_x, "-r")
		pylab.ylim([0,100])
		fig2 = plt.gcf()
	#	plt.show()
		plt.draw()
		fig2.savefig(path_to_file+"/"+q + "-" + start_time+"-RAW.svg")
		break
		#plt.plot(s_times, gr, "-g")
		#pylab.ylim([0,100])
		#fig3 = plt.gcf()
		#plt.show()
		#plt.draw()
		#fig3.savefig(start_time+"/"+q + "-"+start_time+"-growth.svg")


	dt = int(time.time()) - dt_i #current time
	
	#print "---"
	try:
		#count mentions
		for a in (tweet['entities']["user_mentions"]):
			#print "@" + a["screen_name"].encode('ascii', 'ignore')
			
			_b = a["screen_name"].encode('ascii', 'ignore')
			temp_indices.append(a["indices"])
			if _b not in _denm:
				_denm[_b] = 1 #initialise freq counter
			else:
				_denm[_b] += 1 #increase freq with appearance

		#count entities
		for a in (tweet['entities']["hashtags"]):
			#print "#" + a["text"].encode('ascii', 'ignore')
			_b = a["text"].encode('ascii', 'ignore')
			if _b not in _denh:
				_denh[_b] = 1 #similar to above
			else:
				_denh[_b] += 1
	except IndexError:
		pass

	
	table_raw.add_row([str(dt), tweet['id'], tweet['text'].encode('ascii', 'ignore')])		
	ttt = tweet['text'].encode('ascii', 'ignore') #temporary tweet text
	ttt = ttt.split()
#	print ttt
	et = ''
	for a in ttt:
		if a[:1] == "#" or a[:1] == "@" or a[:4] == "http":
			pass
		else:
			et += a + " "
	#print et
	et = tokenizer.tokenize(et)
	for a in range(len(et)): #deals with capital letters
		et[a] = et[a].lower()
	f_t = [w for w in et if not w in stopwords.words('english')] #remove stopwords for vector analysis
	#hashtags are included, might as well remove mentions and links before this (completed)
	et = ''
	for a in f_t:
		et += a + " "
	#print f_t
	for a in f_t:
		if a not in vocab:
			vocab[a] = 1
		else:
			vocab[a] += 1
		if a not in temp_vocab:
			temp_vocab[a] = {}
			temp_vocab[a]["freq"] = 1
		else:
			temp_vocab[a]["freq"] += 1

	table_nontrivial.add_row([str(dt), tweet['id'], et])
	#print f_t

	#now implt tf idf sorting
	#idf:
	for a in temp_vocab:
		temp_vector[a] = math.log(t_x/vocab[a])
	#print pp(temp_vector)

	#tf:
	for a in temp_vocab:
		temp_vocab[a]['ti'] = {}
		temp_vocab[a]['ti'] = vocab[a] * temp_vector[a]
	t_vectors[tweet['id']] = {}
	t_vectors[tweet['id']]['length'] = math.sqrt(sum(temp_vocab[a]['ti']**2 for a in temp_vocab))
	t_vectors[tweet['id']]['ti_table'] = {}
	for a in temp_vocab:
		t_vectors[tweet['id']]['ti_table'][a] = temp_vocab[a]['freq']
	print pp(t_vectors)
	try:
		dt == prev #is this tweet the same bin as the previous one?
	except NameError: #only happens for 1st tweet		
		prev = dt
		continue
	#print "dt is " + str(dt)
	#print "prev is " + str(prev)

	temp_vocab = {}
	temp_vector = {}

	if dt == prev: #if same bin
		tc += 1 #increase number in bin
		#print "tc is " + str(tc)
	else: #if not same bin --> NEXT BIN/SECOND, MOVING ON NOW
	#hashtags part
		#print pp(_denh)
		#print "length of vocab is :" + str(len(vocab))
		while any(a not in t_ha for a in _denh):
			for a in _denh:
				if a not in t_ha:
					#print a + " is missing"
					t_ha[a] = {}
					t_ha[a][prev] = _denh[a]
				else:
					t_ha[a][prev] = _denh[a]
		#print "after \n" + pp(t_ha)
		"""while any(a not in _denh for a in t_ha):
			for a in t_ha:
				if a not in _denh:
					t_ha[a].append(0)
					_denh[a] = 0
		
		print "NEXT """

		#print temp_vocab 


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
		"""if c > 9:
			try:
				gr.append((s_t - s_s[c - 10])/s_s[c-10])
				if gr[-1] > 15:
					print "something's happening"
			except ZeroDivisionError:
				gr.append(None)
		
		#you should apply EMA to to growth to weigh the past 100 or so tweets... above code is kinda unreliable
		else:
			gr.append(None)
		"""

		#p_d.append([dt, tc])
		#one step toward scompletion wow
		c += 1
		#clear your lovely variables
		tc = 0
		_denm = {}
		_denh = {}

		prev = dt
	
	#progress indicator
	"""load_text = "[" + int(c/float(lim) * 100 - 1) * "=" + ">" + (100 - int(c/float(lim) * 100)) * " " + "] (" + str(c) + " out of " + str(lim) + ")"
	try:
		if not load_text == prev_load_text:
			print load_text
	except NameError:
		pass
	prev_load_text = load_text
	"""

		#save_to_mongo(tweet, "time-series", str(int(time.time())))
	
	
