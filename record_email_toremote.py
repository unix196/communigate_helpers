#!/usr/bin/python -u
# -*- coding: utf8 -*-
import fileinput
from sys import stdin
import sys
import os
import datetime
import re
import random 
from email.parser import Parser
from email.header import decode_header
import json
import requests


def post_processing_file(filename):

	info_dict = {}
	recipient_list = []

	os.system(": > /tmp/temp_email.log")

	f = open(filename, 'r')
	for line in f:
	#поиск  служебной инфы, которую предоставил cgate
		p = re.compile('\w{1}\s')  # если строка начинается на одну букву, потом пробел
		#другие шаблоны для поиска (инфа с cgate)
		p_source_ip = re.compile('S\s')
		p_return_path_cgate = re.compile('P\s')
		p_recipient = re.compile('R\s')

		if p.match(line):
			line_sep=line.split()
			if p_source_ip.match(line):
				#source_ip = line_sep[-1] [94.253.8.106]
				source_ip=re.split("\[(.*)\]",line_sep[-1])  #парсим, чтобы потом убрать символы [ и ]
				#info.append("SourceIP: " + str(source_ip))
				info_dict['SourceIP'] = str(source_ip[1])
			elif p_return_path_cgate.match(line):
				return_path =  line_sep[-1]
				#info.append("Return-path: " + str(return_path))
				info_dict['Return-path'] = str(return_path)
			elif p_recipient.match(line):
				recipient = line_sep[-1]
				#info.append("Recipient: " + str(recipient))
				recipient_list.append(str(recipient))
		else:
			if not line == "\n":
				f_temp = open("/tmp/temp_email.log", 'a')
	                        f_temp.write(line)

		headers = Parser().parse(open("/tmp/temp_email.log", 'r'))

	info_dict['Recipient'] = str(recipient_list)
	info_dict['Date'] = str(headers['date'])
	info_dict['From'] = str(headers['from'])
	info_dict['To'] = str(headers['to'])
	info_dict['Subject'] = str(headers['subject'])
	info_dict['Message-ID'] = str(headers['message-id'])
	
	try:
		a=json.dumps(info_dict, indent=4)

		f_summ = open("/tmp/email.log",'a')
		f_summ.write(str(a)+"\n")
		#код для отправки post запроса на удаленный сервер
		url = 'https://YOUR_SITE/scan/mails.php'
		headers = {'content-type': 'application/json', 'Accept': 'text/plain'}
		r = requests.post(url, data=json.dumps(info_dict), headers=headers)

		#f_summ.write(str(type(info_dict))+"\n")

	except:
		e = sys.exc_info()[0]
		f_summ = open("/tmp/email.log",'a')
		f_summ.write(str(e)+"\n")


def process_file(queue_msg):
	x = random.randint(1,100000)
	count=0
	now_date=datetime.date.today()
	now_time = datetime.datetime.now()
	#current_date = str(now_time.hour)+ "." + str(now_time.minute) + "." + str(now_time.second) + "_" + str(now_time.day) + "-" + str(now_time.month) + "-" + str(now_time.year)
	current_date = str(now_date.day) + "-" + str(now_date.month) + "-" + str(now_date.year)
	filename="/tmp/email_data."+current_date+"_"+str(x)+".txt"
	f = open(filename, 'a')
	for line in open(queue_msg):
		if  line == "\n":
			count=count+1
		#если встречаем второй пробел, то перестаем дальше смотреть письмо
		if count == 2:
			break
		f.write(line)
	f.close()
	post_processing_file(filename)	
	os.remove(filename)

while (1):
	line = stdin.readline()
	if not line:
		break
	sys.stdout.write(line)
	line_sep=line.split()

	if  len(line_sep) > 1:
		if line_sep[1] == "FILE":
			queue_msg=line_sep[2]
        	        process_file(queue_msg)
		else: print "Unknown command"


