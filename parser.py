from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import datetime
import csv
import requests


class Parser():
	"""docstring for Parser"""
	TELEGRAM_TOKEN = "token"
	TELEGRAM_CHATID = "chatid"

	def __init__(self, ignore_file="BountyList.csv", start_url='https://bitcointalk.org/index.php?board=238.'):
		options = Options()
		options.add_argument("--headless")
		self.driver = webdriver.Firefox(firefox_options=options)
		self.ignore_file = ignore_file
		self.start_url = start_url
		self.counter = 0
		super(Parser, self).__init__()

	def start(self, number_of_pages):
		""" number_of_pages containes how many pages to you want to parse """
		self.bountylist = self.get_ignore_list()
		for i in range(number_of_pages):
			bounties = get_bounties(self.start_url + str(i*40))
			for j in range(len(bounties)):
				if self.check_date(bounties[j][-1]):
					self.counter +=1
					self.telegram(bounties[j])
					self.bountylist.append(bounties[j][-1])
					self.add_to_file(bounties[j])
		self.driver.quit()

	def get_ignore_list(self):
		""" gets a list of lines in a file """
		with open(self.ignore_file, "r") as ff:
			return [line.strip() for line in ff]

	def add_to_ignore_list(self, bounty):
		""" adds newly checked bounties to BountyList.csv file """
		with open(self.ignore_file, 'a', newline='') as ff:
			b = csv.writer(ff, delimiter=',')
			b.writerow(bounty[3:])

	def get_page_source(self, url):
		""" gets source html of a page by its URL """
		try:
			self.driver.get(url)
			element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/table[1]/tbody/tr/td[1]/span")))
		finally:
			return self.driver.page_source

	def get_bounties(self, url):
		""" generates a list of all bounties from bitcointalk """
		html = self.get_page_source(url)
		junk = BeautifulSoup(html, "html.parser")
		menu = junk.findAll("div", {"class":"tborder"})
		pups = menu[1].findAll("tr")
		all_bounties = [pup.findAll("td", {"class":"windowbg"}) for pup in pups if len(pup.findAll("td", {"class":"windowbg"}))>0]

		for n in range(len(all_bounties)):
			all_bounties[n] = all_bounties[n][0].findAll("span") + all_bounties[n][1:]
			all_bounties[n].extend([all_bounties[n][0].a["href"]])
			for m in range(len(all_bounties[n])-1):
				if m<len(all_bounties[n]):
					all_bounties[n][m]=all_bounties[n][m].text.strip()

		new_bounties = [bounty for bounty in all_bounties
			if bounty[-1] not in self.bountylist
			and "bounty" in bounty[0].lower()
			# and int(bounty[-2])<5000
			# and int(bounty[-3])<1000
			# additional search criterias can be added here
		]
		return new_bounties

	def check_date(self, url):
		""" checks if the bounty is less than seven days old """
		html = self.get_page_source(url)
		junk = BeautifulSoup(html, "html.parser")
		step1 = junk.find("td", {"class":"td_headerandpost"})
		step2 = step1.find("div", {"class":"smalltext"})
		try:
			kapusta = step2.text
			if "today" in kapusta.lower(): # or (datetime.datetime.now() - datetime.datetime.strptime(kapusta, '%B %d, %Y, %I:%M:%S %p')).days <=7:
				return True
			elif (datetime.datetime.now() - datetime.datetime.strptime(kapusta, '%B %d, %Y, %I:%M:%S %p')).days <=7:
				return True
			else:
				return False
		except Exception as e:
			print("ERROR:", e)
			return False

	def telegram(self, bounty):
		""" send links to new bounties to a telegram group """
		url = "https://api.telegram.org/bot{token}/{method}?chat_id={chat_id}&text=".format(
			token = self.TELEGRAM_TOKEN,
			method = "sendMessage",
			chat_id = self.TELEGRAM_CHATID)

		url = url + "{one}) {two}\n{three}".format(
			one = self.counter,
			two = bounty[0].replace("$","").replace("#","").replace("&",""),
			three = bounty[-1])
		requests.post(url)