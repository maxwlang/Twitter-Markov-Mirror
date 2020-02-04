#!/usr/bin/env python
# encoding: utf-8

import markovify, threading, urllib2, string, tweepy, json, time, sys, os

#Twitter API credentials
consumer_key = "" # Find at developer.twitter.com
consumer_secret = "" # Find at developer.twitter.com
access_key = "" # Find at developer.twitter.com
access_secret = "" # Find at developer.twitter.com

twitter_handle = "" # Twitter handle of the person we're mimicking.
twitterbot_handle = "" # Twitter handle of your bot.

tweet_timer = 600 # Seconds between each tweet.
refresh_timer = 3600 # Seconds between updating tweet database.
similarity_timer = 1200 # Seconds between looking for updated profile data.


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

recent_twitter_color = {
	'profile_background_color': "Nothing",
	'profile_text_color': "Nothing",
	'profile_link_color': "Nothing",
	'profile_sidebar_fill_color': "Nothing",
	'profile_sidebar_border_color': "Nothing"
} # Don't change this

def downloadFile(url, file_name):
	uopener = urllib2.build_opener()
	u = uopener.open(url)
	meta = u.info()
	remote_file_size = int(meta.getheaders("Content-Length")[0])
	
	if(os.path.isfile("./"+file_name)):
		print "Comparing local file with remote file for %s.." % (file_name)
		local_file_size = os.path.getsize("./"+file_name)
		if(remote_file_size != local_file_size):
			print("Files do not match! Downloading..")
			f = open("./"+file_name, 'wb')
			print "Downloading: %s Bytes: %s" % (file_name, remote_file_size)

			file_size_dl = 0
			block_sz = 8192
			while True:
				buffer = u.read(block_sz)
				if not buffer:
					break

				file_size_dl += len(buffer)
				f.write(buffer)
				status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / remote_file_size)
				status = status + chr(8)*(len(status)+1)
				print status,

			f.close()
			return True
		else:
			print("Files match! Skipping..")
			return False
	else:
		f = open("./"+file_name, 'wb')
		print "Downloading: %s Bytes: %s" % (file_name, remote_file_size)

		file_size_dl = 0
		block_sz = 8192
		while True:
			buffer = u.read(block_sz)
			if not buffer:
				break

			file_size_dl += len(buffer)
			f.write(buffer)
			status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / remote_file_size)
			status = status + chr(8)*(len(status)+1)
			print status,

		f.close()
		return True
			
def get_all_tweets(screen_name):
	threading.Timer(refresh_timer, get_all_tweets, [screen_name]).start()
	
	print('Just a second, I\'m updating my brain..')
	
	#Twitter only allows access to a users most recent 3240 tweets with this method
	alltweets = []	
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)
	alltweets.extend(new_tweets)
	oldest = alltweets[-1].id - 1
	
	while len(new_tweets) > 0:
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
		alltweets.extend(new_tweets)
		oldest = alltweets[-1].id - 1
		
		status = r" %d tweets downloaded.." % (len(alltweets))
		status = status + chr(8)*(len(status)+1)
		print status,
		print("") # Update terminal buffer

	print("\n Done.")

	outtweets = [[tweet.text.encode("utf-8")] for tweet in alltweets]

	with open("./"+screen_name+"_brain.json", 'wb') as f:
		f.seek(0)
		f.write(json.dumps(outtweets))

	print('My brain has been updated with the latest tweets.')
	pass

def update_account_similarity(screen_name):
	threading.Timer(similarity_timer, update_account_similarity, [screen_name]).start()
	print('> Account similarity check')
	
	user = api.get_user(twitter_handle)
	
	try:
		if(user.profile_use_background_image):
			print('>> Checking background image')
			if(downloadFile(user.profile_background_image_url_https, './'+twitter_handle+'_background.png')):
				api.update_profile_background_image('./'+twitter_handle+'_background.png')
		
		print('>> Checking banner image')
		if(downloadFile(user.profile_banner_url, './'+twitter_handle+'_banner.png')):
			api.update_profile_banner('./'+twitter_handle+'_banner.png')
	
		if(user.default_profile_image != True):
			print('>> Checking profile image')
			url = user.profile_image_url_https.replace('_normal', '')
			if(downloadFile(url, './'+twitter_handle+'_profile.png')):
				api.update_profile_image('./'+twitter_handle+'_profile.png')
	
		print('>> Checking profile color')
		if(recent_twitter_color['profile_background_color'] != user.profile_background_color):
			print('>>> ' + recent_twitter_color['profile_background_color'] + ' -> ' + user.profile_background_color)
			api.update_profile_colors(profile_background_color=user.profile_background_color)
			recent_twitter_color['profile_background_color'] = user.profile_background_color
			
		if(recent_twitter_color['profile_text_color'] != user.profile_text_color):
			print('>>> ' + recent_twitter_color['profile_text_color'] + ' -> ' + user.profile_text_color)
			api.update_profile_colors(profile_text_color=user.profile_text_color)
			recent_twitter_color['profile_text_color'] = user.profile_text_color
			
		if(recent_twitter_color['profile_link_color'] != user.profile_link_color):
			print('>>> ' + recent_twitter_color['profile_link_color'] + ' -> ' + user.profile_link_color)
			api.update_profile_colors(profile_link_color=user.profile_link_color)
			recent_twitter_color['profile_link_color'] = user.profile_link_color
			
		if(recent_twitter_color['profile_sidebar_fill_color'] != user.profile_sidebar_fill_color):
			print('>>> ' + recent_twitter_color['profile_sidebar_fill_color'] + ' -> ' + user.profile_sidebar_fill_color)
			api.update_profile_colors(profile_sidebar_fill_color=user.profile_sidebar_fill_color)
			recent_twitter_color['profile_sidebar_fill_color'] = user.profile_sidebar_fill_color
			
		if(recent_twitter_color['profile_sidebar_border_color'] != user.profile_sidebar_border_color):
			print('>>> ' + recent_twitter_color['profile_sidebar_border_color'] + ' -> ' + user.profile_sidebar_border_color)
			api.update_profile_colors(profile_sidebar_border_color=user.profile_sidebar_border_color)
			recent_twitter_color['profile_sidebar_border_color'] = user.profile_sidebar_border_color
		
	except Exception, e:
		print(">> update_account_similarity failed. "+ str(e))

def load_brain(screen_name):
	with open("./"+twitter_handle+"_brain.json") as f:
		 brain_contents = f.read()
	return brain_contents
	
def send_tweet(screen_name):
	threading.Timer(tweet_timer, send_tweet, [screen_name]).start()
	brain = load_brain(screen_name)
	think = markovify.Text(brain)
	tweet = think.make_short_sentence(140)

	api.update_status(tweet)
	
if __name__ == '__main__':
	print('>>>>> I am literally '+twitter_handle+' <<<<<')
	
	try:
		print('>>> Starting brain refresh timer.. (' + str(refresh_timer) + ' seconds)')
		get_all_tweets(twitter_handle)
		
		print('>>> Starting account similarity timer.. (' + str(similarity_timer) + ' seconds)')
		update_account_similarity(twitter_handle)
		
		print('>>> Starting Tweet timer.. (' + str(tweet_timer) + ' seconds)')
		send_tweet(twitter_handle)
		
		print('>>> Ok.')
		
		# Basically a pulse
		while True:
			time.sleep(1)
			
	except (KeyboardInterrupt, SystemExit):
		print('\n>>> Goodbye.')
		sys.exit()
		raise