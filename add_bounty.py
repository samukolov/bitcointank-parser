from oauth2client.service_account import ServiceAccountCredentials
import gspread
import urllib.request
from tkinter import *
import datetime
import calendar
import os
from os.path import join
import requests


#---------------------------------------------------------------------------------------------------------------

def check_up(item):
	item[0][2] = item[1].get()
	if item[0][2] != "":
		item[0][1] = "green"
	down_frame()

#---------------------------------------------------------------------------------------------------------------


def onClick(item):
	for widget in win.winfo_children():
		widget.destroy()

	Label(win, text=item[0], width=20, bg="pink").pack(side=LEFT, anchor=NW)

	v = StringVar()
	entry = Entry(win, width=110, bg="lightgreen", textvariable=v)
	v.set(item[2])
	entry.pack(side=LEFT, anchor=W)
	entry.focus()
	send = (item,entry) 

	"""
	tkvar = StringVar(win)
	choices = { 'Pizza','Lasagne','Fries','Fish','Potatoe'}
	tkvar.set('Pizza')
	popupMenu = OptionMenu(win, tkvar, *choices)
	popupMenu.pack(side=LEFT, anchor=W)
	"""

	save = Button(win, text="Save", bg="pink", command=lambda i=send: check_up(i))
	save.pack(side=LEFT, anchor=NW)
	
	window.bind("<space>", (lambda event: check_up(send)))
	window.bind("<Return>", (lambda event: check_up(send)))

	down_frame()

	return

#---------------------------------------------------------------------------------------------------------------

def save_bounty():
	censor = True
	for element in global_a:
		if element[2] == "":
			censor = False
			break

	if censor:
		scope = ['https://spreadsheets.google.com/feeds']
		creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
		credentials = gspread.authorize(creds)
		sheet = credentials.open('ToAdd')
		worksheet = sheet.worksheet("ToAdd")
		columns = worksheet.get_all_values()
		for i in range(len(global_a)):
			worksheet.update_cell(len(columns)+1, i+1, global_a[i][2])
		refresh()
	else:
		for widget in win.winfo_children():
			widget.destroy()
		Label(win, text="NOT ENOUGHT INFORMATION!!!", bg="red", fg="white", width=156).pack()

#---------------------------------------------------------------------------------------------------------------

def refresh():
	global global_a
	global_a = [['Username','green','oi_ahoy'],
				['Bounty','lightgrey',''],
				['Retweets','lightgrey',''],
				['Tweets','lightgrey',''],
				['Hashtags','lightgrey',''],
				['Due Date','lightgrey',''],
				['Expiration Date','lightgrey',''],
				['Bitcointalk','lightgrey',''],
				['Spreadsheet','lightgrey',''],
				['Telegram 1','lightgrey',''],
				['Telegram 2','lightgrey',''],
				['Comment','lightgrey','']]

	for widget in down.winfo_children():
		widget.destroy()
	for widget in win.winfo_children():
		widget.destroy()
	down_frame()

#---------------------------------------------------------------------------------------------------------------


def down_frame():
	for widget in down.winfo_children():
		widget.destroy()

	for item in global_a:
		button = Button(down, text=item[0], bg=item[1], command=lambda i=item: onClick(i))
		button.pack(side=LEFT)

	Label(down, width=10).pack(side=LEFT)
	Button(down, text="SAVE BOUNTY", bg="yellow", command=save_bounty).pack(side=LEFT)
	Button(down, text="NEW BOUNTY", bg="lightblue", command=refresh).pack(side=LEFT)


#---------------------------------------------------------------------------------------------------------------


def main_frame():
	for widget in down.winfo_children():
		widget.destroy()

	for i in range(len(global_a)):
		Label(win, text=global_a[i][0]).grid(row=i, column=0)

		v = StringVar()
		entry = Entry(win, width=110, bg="lightgreen", textvariable=v)
		v.set(global_a[i][2])
		entry.grid(row=i, column=1)
		entry.focus()


#---------------------------------------------------------------------------------------------------------------


window = Tk()
#window.state('zoomed')
window.wm_title('Хруст Бабоса')

# get screen width and height
ws = window.winfo_screenwidth() # width of the screen
hs = window.winfo_screenheight() # height of the screen

w = 130 # width for the Tk root
h = 252+100 # height for the Tk root

# calculate x and y coordinates for the Tk window window
x = (ws-w-40)
y = (70)

# set the dimensions of the screen 
# and where it is placed
window.geometry('%dx%d+%d+%d' % (w, h, x, y))
window.attributes('-topmost', 'true')

win = Frame(window)
win.pack(anchor=W)
#Label(win, bg="pink", width=156).pack()

down = Frame(window)
down.pack(side=BOTTOM, anchor=W)


global_a = [['Username','green','oi_ahoy'],
			['Bounty','lightgrey',''],
			['Retweets','lightgrey',''],
			['Tweets','lightgrey',''],
			['Hashtags','lightgrey',''],
			['Due Date','lightgrey',''],
			['Expiration','lightgrey',''],
			['Bitcointalk','lightgrey',''],
			['Spreadsheet','lightgrey',''],
			['Telegram 1','lightgrey','nope'],
			['Telegram 2','lightgrey','nope'],
			['Comment','lightgrey','']]

main_frame()
#down_frame()

window.mainloop()




#--------------------------------------------------------------------------------------------------------------------
