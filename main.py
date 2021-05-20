# Cross-platform import system log (Windows 10, Debian, Ubuntu)
# Version 1.0

# Modules import
import platform
import socket
import subprocess
import paramiko
import time
import os

# networkscan function declare
def networkscan():
	# split network address into list from user input
	net = input("Enter the Network Address: ")
	net1= net.split('.')
	a = '.'
	net2 = net1[0] + a + net1[1] + a + net1[2] + a
	st1 = int(input("Enter the Starting digit of the network (/24): "))
	en1 = int(input("Enter the Last digit of the network (/24): "))
	en1 = en1 + 1

	# ping request construction according to the system/OS on which the program is being currently executed 
	# platform.system() returns the system/OS name
	global osplatform
	osplatform = platform.system()
	if (osplatform == "Windows"):
		ping1 = "ping -n 1 "
	else:
		ping1 = "ping -c 1 "

	# dictionary init
	dict_IP_Online ={}
	# ping loop through the IP address range
	for host in range(st1,en1):
		addr = net2 + str(host)
		comm = ping1 + addr
		response = subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE).communicate()[0]
		
		# dictionary updated with the hostname and ip address of the reachable machines
		# socket.gethostbyaddr() returns a tuple containing hostname, alias list and IP address of the host 
		# if statement on string 'TTL=' response used for Windows system
		if 'TTL=' in str(response):
			# the try block process socket.gethostbyaddr() on ip address
			try:
				hostName = socket.gethostbyaddr(addr)
			# the except block process in case of the error.
			except socket.herror:
				hostName =("Unknown",)
			dict_IP_Online.update({hostName[0]:addr})
		# if statement on string 'ttl=' response used for Unix system
		elif 'ttl=' in str(response):
			# the try block process socket.gethostbyaddr() on ip address
			try:
				hostName = socket.gethostbyaddr(addr)
			# the except block process in case of the error.
			except socket.herror:
				hostName =("Unknown",)
			dict_IP_Online.update({hostName[0]:addr})

	print()

	# if statement evaluate empty dictionary
	if bool(dict_IP_Online) is False:
		print("All IP are offline or unreachable")
		exit()
	# else statement print table from dictionary 
	else:
		equal = '=' * 40
		dash = '-' * 40
		print(equal)
		print("{: ^1}{: ^18}{: ^2}{: ^18}{: ^1}".format("|","Hostname","||", "IP","|"))
		print(equal)
		# loop on key and value from dictionary to print the table
		for key, value in dict_IP_Online.items():
			print("{: ^1}{: ^18}{: ^2}{: ^18}{: ^1}".format("|",key,"||", value,"|"))
			print(dash)

	print()

	# while loop execute input as long as ip entered is not in dictionary value
	global hostip
	hostip = input("Enter IP address from the list to initiate the SSH connection? ? (x to exit) ")
	while hostip not in dict_IP_Online.values():
		if hostip == "x":
		 	exit()
		else:
			hostip = input("Please, enter IP address from the list to initiate the SSH connection? (x to exit) ")

	# global variable containing the value of the key associated with the value of ip entered 
	global computerName
	computerName = list(dict_IP_Online.keys())[list(dict_IP_Online.values()).index(hostip)]
	
# runningSSH function declare
def runningSSH ():
	# while loop execute function as long as is true
	runningSSH = True
	while runningSSH:
		# while loop execute input username until is not empty
		username = ""
		while username == "":
			username = input("Enter the {} SSH login ? (x to exit) ".format(computerName))
			if username == "x":
				exit()
		# while loop execute input password until is not empty
		password = ""
		while password == "":
			password = input("Enter the {} SSH password ? (x to exit) ".format(computerName))
			if password == "x":
				exit()
		# the try block process ssh connect with paramiko module
		try:
			# create a new SSHClient
			ssh = paramiko.SSHClient()
			# policy as paramiko.AutoAddPolicy() to allow the Python script to SSH to a remote server with unknown SSH keys
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			# connect the client to the host with the credentials username and password
			ssh.connect(hostip, username=username, password=password)
			# execute the command on the remote host and return a tuple containing the stdin, stdout, and stderr from the host
			# command get OS system version
			command= "wmic os get Caption /value"
			stdin,stdout,stderr=ssh.exec_command(command)
			# call paramiko.channel.ChannelFile.read() with paramiko.channel.ChannelFile as stdout to return the output from the command
			# output is decode to cp437 for windows console
			stdout=stdout.read().decode ("cp437")
			# string format time from local time 
			timestr = time.strftime("%Y%m%d-%H%M%S")
			# if statement on string 'Windows' stdout
			if 'Windows' in str(stdout):
				# execute the command on the remote host and return a tuple containing the stdin, stdout, and stderr from the host
				# command export windows system log on remote host 
				command= "wevtutil epl System %temp%\\" + timestr + "_" + computerName + "_System_log.evtx"
				stdin,stdout,stderr=ssh.exec_command(command)
				# recv_exit_status() return the exit status from the process
				# if the command hasn’t finished yet, this method will wait until it does
				exit_status = stdout.channel.recv_exit_status()       
				if exit_status == 0:
					# file transfers handled by open_sftp() on ssh instance of Paramiko.SSHClient
					sftp = ssh.open_sftp()
					# remote file path
					filepath = "C:\\Users\\" + username + "\\AppData\\Local\\Temp\\" + timestr + "_" + computerName + "_System_log.evtx"
					# if statement on Windows returns platform.system()
					if (osplatform == "Windows"):
						# create newpath on local host where script is being currently executed if not already exist
						newpath = "C:\\temp\\"
						if not os.path.exists(newpath):
							os.makedirs(newpath)
						# local file path in case of currently executed script is Windows
						localpath = "C:\\temp\\" + timestr + "_" + computerName + "_System_log.evtx"
					else:
						# local file path in case of currently executed script is not Windows
						localpath = "/tmp/" + timestr + "_" + computerName + "_System_log.evtx"		
					# downloading file from remote machine
					sftp.get(filepath,localpath)
				# else exit status is provided by the server
				else:
					print("Error with SSH command", exit_status)
			# else statement on stdout
			else:				
				# execute the command on the remote host and return a tuple containing the stdin, stdout, and stderr from the host
				# command export system log on remote host if host is not Windows
				command= "cp /var/log/syslog /tmp/" + timestr + "_" + computerName + "_syslog"
				stdin,stdout,stderr=ssh.exec_command(command)
				exit_status = stdout.channel.recv_exit_status()
				# recv_exit_status() return the exit status from the process
				# if the command hasn’t finished yet, this method will wait until it does       
				if exit_status == 0:
					# file transfers handled by open_sftp() on ssh instance of Paramiko.SSHClient
					sftp = ssh.open_sftp()
					# remote file path
					filepath = "/tmp/" + timestr + "_" + computerName + "_syslog"
					# if statement on Windows returns platform.system()
					if (osplatform == "Windows"):
						# create newpath on local host where script is being currently executed if not already exist
						newpath = "C:\\temp\\"
						if not os.path.exists(newpath):
							os.makedirs(newpath)
						# local file path in case of currently executed script is Windows
						localpath = "C:\\temp\\" + timestr + "_" + computerName + "_syslog"
					else:
						# local file path in case of currently executed script is not Windows
						localpath = "/tmp/" + timestr + "_" + computerName + "_syslog"
					# downloading file from remote machine
					sftp.get(filepath,localpath)
				# else exit status is provided by the server
				else:
					print("Error with SSH command", exit_status)
			# print location of downloading file
			print()
			print("Your system log can be found in : {}".format(localpath))
			# while statement put to false to stop the loop
			runningSSH = False
			# close sftp connection if exist
			if sftp: sftp.close()
			# close ssh connection if exist
			if ssh: ssh.close()
		# the except block process in case on ssh port closed and break the loop
		except paramiko.ssh_exception.NoValidConnectionsError as error:
			print(error)
			break
		# the except block process in case on authentification issues and pass the loop
		except paramiko.ssh_exception.AuthenticationException as error:
			print(error)
			pass
# calling of function networkscan
networkscan()
# calling of function runningSSH
runningSSH()