from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import datetime
import csv
import requests

def get_file(file):
	""" gets a list of lines in a file """
	a=[]
	f = open(file, "r")
	for line in f:
		a.append(line.strip())
	f.close()
	return a

def backup_files(backup):
	""" adds newly checked bounties to BountyList.csv file """
	with open("BountyList.csv", 'a', newline='') as fp:
		b = csv.writer(fp,delimiter=',')
		b.writerow(backup[3:])
	fp.close()

def telegram(bounty):
	""" sends links to new bounties to a telegram group """
	url = "https://api.telegram.org/bot{token}/{method}?chat_id={chat_id}&text=".format(
		token="token",
		method="sendMessage",
		chat_id="chatid")

	url = url + "{one}) {two}\n{three}".format(
		one = str(counter),
		two = bounty[0].replace("$","").replace("#","").replace("&",""),
		three = bounty[-1])
	requests.post(url)

def get_urls(url):
	""" generates a list of all bounties from bitcointalk """
	ff.get(url)
	try:
		element = WebDriverWait(ff, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/table[1]/tbody/tr/td[1]/span")))
	finally:
		html = ff.page_source
		#ff.quit()

	junk = BeautifulSoup(html, "html.parser")
	menu = junk.findAll("div", {"class":"tborder"})
	pups = menu[1].findAll("tr")


	all_bounties = [pup.findAll("td", {"class":"windowbg"}) for pup in pups 
		if len(pup.findAll("td", {"class":"windowbg"}))>0]

	for n in range(len(all_bounties)):
		all_bounties[n] = all_bounties[n][0].findAll("span") + all_bounties[n][1:]
		all_bounties[n].extend([all_bounties[n][0].a["href"]])

		for m in range(len(all_bounties[n])-1):
			if m<len(all_bounties[n]):
				all_bounties[n][m]=all_bounties[n][m].text.strip()

	new_bounties = [bounty for bounty in all_bounties
		if bounty[-1] not in bountylist
		and "bounty" in bounty[0].lower()] # additional search criterias can be added here
	#and int(bounty[-2])<5000
	#and int(bounty[-3])<1000

	return new_bounties

def check_date(url):
	""" checks if the bounty is less than seven days old """
	ff.get(url)
	try:
		element = WebDriverWait(ff, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/table[1]/tbody/tr/td[1]/span")))
	finally:
		html = ff.page_source
		#ff.quit()

	junk = BeautifulSoup(html, "html.parser")
	#step1 = junk.findAll("div", {"id":"bodyarea"})
	#step2 = step1.findAll("form")
	step1 = junk.find("td", {"class":"td_headerandpost"})
	step2 = step1.find("div", {"class":"smalltext"})

	try:
		kapusta = step2.text
	except Exception as e:
		print("ERROR", e)
		print(step2)
		print(step2.text)


	if "oday" not in kapusta or (datetime.datetime.now() - datetime.datetime.strptime(kapusta, '%B %d, %Y, %I:%M:%S %p')).days <=7:
		return True
	return False

#--------------------------------------------------------------------------------------------------------------------

bountylist = get_file("BountyList.csv")

options = Options()
options.add_argument("--headless")
ff = webdriver.Firefox(firefox_options=options)
#ff = webdriver.Firefox()

counter=1
for i in range(50):
	try:
		bounties = get_urls('https://bitcointalk.org/index.php?board=238.' + str(i*40))

		for j in range(len(bounties)):
			try:
				if check_date(bounties[j][-1]):
					telegram(bounties[j])
					counter = counter+1
					print("Telegram")
					bountylist.append(bounties[j][-1])
					backup_files(bounties[j])

			except Exception as e:
				print(e)

	except Exception as e:
		print(e)

ff.quit()
