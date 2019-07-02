from oauth2client.service_account import ServiceAccountCredentials
import gspread
import tweepy
import datetime
import random
import time
import requests


#--------------------------------------------------------------------------------------------------------------------

# gets a list of credentials for each twitter account
def get_accounts():
	try:
		scope = ['https://spreadsheets.google.com/feeds']
		creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
		client = gspread.authorize(creds)
		sheet = client.open('Accounts')
		worksheet = sheet.worksheet("Sheet1")
		local_a = worksheet.get_all_values()
		return local_a
	except Exception as e:
		print(e)


#--------------------------------------------------------------------------------------------------------------------

# logs in to twitter with given credentials
def twitter_login(name):
	auth = tweepy.OAuthHandler(name[3], name[4])
	auth.set_access_token(name[1], name[2])
	api = tweepy.API(auth, wait_on_rate_limit=True)
	return api


#-------------------------------------------------------------------------------------------------------------------

# sends a telegram message
def telegram(text):
	url = "https://api.telegram.org/bot{token}/{method}?chat_id={chat_id}&parse_mode={parse_mode}&text=".format(
		token="token",
		method="sendMessage",
		parse_mode="HTML",
		chat_id="chat id")

	url=url+text
	requests.post(url)


#--------------------------------------------------------------------------------------------------------------------

"""
sets a status for each account. 
	"0" - all good and new followers can be added.
	"1" - following too many people, removes users that do not follow you back
	"suspended" - twitter token has to be regenerated
"""
def update_status(status):
	scope = ['https://spreadsheets.google.com/feeds']
	creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
	credentials = gspread.authorize(creds)
	sheet = credentials.open('Accounts')
	worksheet = sheet.worksheet("Sheet1")
	worksheet.update_cell(i+1, 9, status)


#-------------------------------------------------------------------------------------------------------------------

"""
checks status for each account. 
	"0" - all good and new followers can be added.
	"1" - following too many people, removes users that do not follow you back
	"suspended" - twitter token has to be regenerated
"""
def check_status():
	for i in range(len(names)):
		print(names[i][0])
		if names[i][0] != "oiwazowski":
			try:
				api = twitter_login(names[i])

				user = names[i][0]
				i_follow = [item for item in tweepy.Cursor(api.friends_ids, screen_name=user).items(10000)]
				followers = [item for item in tweepy.Cursor(api.followers_ids, screen_name=user).items(10000)]
				ratio = len(i_follow)/len(followers)

				print("Followers:", len(followers))
				print("Following:", len(i_follow))
				print("Overload:{}%".format(int(ratio*100)-100))
				print()
			except Exception as e:
				print(e)


#-------------------------------------------------------------------------------------------------------------------


# stops following people that do not follow you back
def remove_friends():

	bastards = [item for item in i_follow if item not in followers]
	counter=0
	for z in range(len(bastards)):
		try:
			api.destroy_friendship(bastards[z])
			counter=counter+1
			
		except Exception as e:
			error = e.args[0][0]['code']
			if error not in [34,50,63,108,158,160]:
				telegram("{}: <b>{}</b>".format(user, e))
				update_status("Suspended")
				break


#-------------------------------------------------------------------------------------------------------------------

# searches for random Twitter users and follows them
def add_friends():
	a = [item for item in followers if item not in i_follow]
	limit = min(20,len(a))
	counter = 0
	for z in range(limit):
		try:
			api.create_friendship(a[z])
			counter=counter+1
		
		except Exception as e:
			error = e.args[0][0]['code']
			if error not in [34,50,63,108,158,160]:
				telegram("{}: <b>{}</b>".format(user, e))
				update_status("Suspended")
				break

	if counter<20 and user!="oi_ahoy":
		angels = api.followers_ids(followers[random.randint(0,len(followers)-1)])
		b = [item for item in angels if item not in i_follow]
		limit=0
		for x in range(20-counter):
			try:
				api.create_friendship(angels[x])
				limit=limit+1

			except Exception as e:
				error = e.args[0][0]['code']
				if error not in [34,50,63,108,158,160]:
					Telegram("{}: <b>{}</b>".format(user, e))
					update_status("Suspended")
					break


#-------------------------------------------------------------------------------------------------------------------


pigs = [] # list of accounts that you would like to manage
names = get_accounts()


#------> MAIN BODY <------
for i in range(len(names)):
	for m in range(len(pigs)):
		if names[i][0] == pigs[m] and names[i][8] != "Suspended":
			try:
				api = twitter_login(names[i])

				user = names[i][0]
				i_follow = [item for item in tweepy.Cursor(api.friends_ids, screen_name=user).items(10000)]
				followers = [item for item in tweepy.Cursor(api.followers_ids, screen_name=user).items(10000)]
				ratio = len(i_follow)/len(followers)

				if ratio>1.2 and len(i_follow)>1000:
					update_status("1")
					names[i][8] = "1"

				if ratio<=1:
					update_status("0")
					names[i][8] = "0"

				if names[i][8] == "0":
					add_friends()

				elif names[i][8] == "1":
					remove_friends()
				
			except tweepy.TweepError as e:
				error = e.args[0][0]['code']
				if error not in [34,50,63,108,158,160]:
					telegram("{}: <b>{}</b>".format(names[i][0], e))
					update_status("Suspended")
			except Exception:
				pass