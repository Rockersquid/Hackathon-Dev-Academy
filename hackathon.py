#!/usr/bin/env python
#started a python mail server using : python -m smtpd -n -c DebuggingServer localhost:1025
#python version 2.7

import httplib
import datetime
import smtplib
import sys
import requests
import socket;
import subprocess
import sched, time

while 1:
	now = datetime.datetime.now()
	if (now.hour > 5 and now.hour < 20):
		print "Now the fun begins."
		smallSysAdmin = "small.sys.admin@gmail.com"
		bigSysAdmin = "big.sys.admin@gmail.com"
		hour = now.hour
		i = 0
		erroCount = 0
		while (hour > 5 and hour < 20):
			#checking to see if server is running
			p1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
			p2 = subprocess.Popen(["grep", "apache"], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			p1.stdout.close()
			out, err = p2.communicate()

			if err:
				#we encountered an error here so we restart apache
				subprocess.check_call("sudo service apache2 restart".split())
				erroCount += 1
				print err

			if "www-data" in out:
				print "Apache is running"
			else:
				#apache was down now restarting it
				print "Apache was down, now starting apache."
				subprocess.check_call("sudo service apache2 restart".split())
				erroCount += 1

			#checking to see if server is listening to port 80
			host = 'hackathon.com'
			port = 80
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				#server is listening to port 80
			 	s.connect((host, port))
			 	s.shutdown(2)
			 	print "Success connecting to "
			 	print host + " on port: " + str(port)
			except:
				#server no longer listening to port 80
				erroCount += 1
				print "Cannot connect to "
			 	print host + " on port: " + str(port)

			#second attempt to see if apache is listening to port 80 using netstat, couldn't get it to work along with grep, it took too long thius i decided to keep the old approach using sockets and directly connecting to the sserver
			# p1 = subprocess.Popen(['netstat', 'anp'], stdout=subprocess.PIPE)
			# p2 = subprocess.Popen(["grep", "apache"], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			# out, err = p1.communicate()
			# print out
			# print err

			#requesting headers to see if the status is ok
			try:
				conn = httplib.HTTPConnection("hackathon.com")
				conn.request("HEAD", "/")
				r1 = conn.getresponse()
				if (r1.status != 200):
					#rserver responded with invalid status
					print "Invalid status."
					erroCount += 1	
				else:
					print r1.status
			except: 
				#server is down restarting apache
				subprocess.check_call("sudo service apache2 restart".split())
				print "Connection refused."; 
				erroCount += 1	
			#checking for keyword
			try:
				ret = requests.get('http://hackathon.com/index.html')
				if ("MERGE" in ret.content):
					print "Keyword found."
				else:
					#didn't find the keyword problems with the page
					print "Keyword not found."
					erroCount += 1
			except requests.exceptions.ConnectionError as e:    # This is the correct syntax
			   erroCount += 1

			print "Error count:"
			print erroCount

			if (erroCount > 0):
				if (erroCount > 5):
					#big problem email
					FROM = 'monty@python.com'
					TO = ["edward.george.ionescu@gmail.com"] # must be a list
					SUBJECT = "Hello!"
					TEXT = "The server is down. I repeat the server is down. All hands on deck."

					# Prepare actual message
					message = """\
					From: %s
					To: %s
					Subject: %s
					%s
					""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
					# Send the mail
					server = smtplib.SMTP('localhost', 1025)
					server.sendmail(FROM, TO, message)
					server.quit()
				else:
					#small problem email
					FROM = 'monty@python.com'
					TO = ["edward.george.ionescu@gmail.com"] # must be a list
					SUBJECT = "Hello!"
					TEXT = "The server has encuntered some errors. Time to check it and see what is wrong."

					# Prepare actual message
					message = """\
					From: %s
					To: %s
					Subject: %s
					%s
					""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
					# Send the mail
					server = smtplib.SMTP('localhost', 1025)
					server.sendmail(FROM, TO, message)
					server.quit()

			now = datetime.datetime.now()
			hour = now.hour
			#i = i +1
			#here we make the program wait 2 minutees before executing the script again
			time.sleep(120)
	else:
		time.sleep(3600)
		print "The server sleeps now, shhh..."

