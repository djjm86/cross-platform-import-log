# Cross-platform import system log (Windows 10, Debian, Ubuntu)
# Version 1.0

# Import des modules
import subprocess
import platform
import socket
import paramiko
import time
import os

# networkscan function declare
def networkscan():
	# split network address into list "net2"
	net = input("Enter the Network Address: ")
	net1= net.split('.')
	a = '.'
	net2 = net1[0] + a + net1[1] + a + net1[2] + a
	st1 = int(input("Enter the Starting digit of the network (/24): "))
	en1 = int(input("Enter the Last digit of the network (/24): "))
	en1 = en1 + 1

	global osplatform
	osplatform = platform.system()
	if (osplatform == "Windows"):
		ping1 = "ping -n 1 "
	else:
		ping1 = "ping -c 1 "

	dict_IP_Online ={}
	for host in range(st1,en1):
		addr = net2 + str(host)
		comm = ping1 + addr
		response = subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE).communicate()[0]
		
		if 'TTL=' in str(response):
			try:
				hostName = socket.gethostbyaddr(addr)
			except socket.herror:
				hostName =("Unknown",)
			dict_IP_Online.update({hostName[0]:addr})
		elif 'ttl=' in str(response):
			try:
				hostName = socket.gethostbyaddr(addr)
			except socket.herror:
				hostName =("Unknown",)
			dict_IP_Online.update({hostName[0]:addr})

	print()

	if bool(dict_IP_Online) is False:
		print("All IP are Offline")
		exit()
	else:
		equal = '=' * 40
		dash = '-' * 40
		print(equal)
		print("{: ^1}{: ^18}{: ^2}{: ^18}{: ^1}".format("|","Host","||", "IP","|"))
		print(equal)
		for key, value in dict_IP_Online.items():
			print("{: ^1}{: ^18}{: ^2}{: ^18}{: ^1}".format("|",key,"||", value,"|"))
			print(dash)

	print()

	global hostip
	hostip = input("Enter IP address from the list to initiate the SSH connection? ? (x to exit) ")
	while hostip not in dict_IP_Online.values():
		if hostip == "x":
		 	exit()
		else:
			hostip = input("Please, enter IP address from the list to initiate the SSH connection? (x to exit) ")

	global computerName
	computerName = list(dict_IP_Online.keys())[list(dict_IP_Online.values()).index(hostip)]
	
# runningSSH function declare
def runningSSH ():
	runningSSH = True
	while runningSSH:
		username = ""
		while username == "":
			username = input("Enter the {} SSH login ? (x to exit) ".format(computerName))
			if username == "x":
				exit()

		password = ""
		while password == "":
			password = input("Enter the {} SSH password ? (x to exit) ".format(computerName))
			if password == "x":
				exit()

		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(hostip, username=username, password=password)

			command= "wmic os get Caption /value"
			stdin,stdout,stderr=ssh.exec_command(command)
			stdout=stdout.read().decode ("cp437")
			timestr = time.strftime("%Y%m%d-%H%M%S")
			if 'Windows' in str(stdout):
				command= "wevtutil epl System %temp%\\" + timestr + "_" + computerName + "_System_log.evtx"
				stdin,stdout,stderr=ssh.exec_command(command)
				exit_status = stdout.channel.recv_exit_status()       
				if exit_status == 0:
					sftp = ssh.open_sftp()
					filepath = "C:\\Users\\" + username + "\\AppData\\Local\\Temp\\" + timestr + "_" + computerName + "_System_log.evtx"
					if (osplatform == "Windows"):
						newpath = "C:\\temp\\"
						if not os.path.exists(newpath):
							os.makedirs(newpath)
						localpath = "C:\\temp\\" + timestr + "_" + computerName + "_System_log.evtx"
					else:
						localpath = "/tmp/" + timestr + "_" + computerName + "_System_log.evtx"			
					sftp.get(filepath,localpath)
				else:
					print("Error with SSH command", exit_status)
			else:
				command= "cp /var/log/syslog /tmp/" + timestr + "_" + computerName + "_syslog"
				stdin,stdout,stderr=ssh.exec_command(command)
				exit_status = stdout.channel.recv_exit_status()       
				if exit_status == 0:
					sftp = ssh.open_sftp()
					filepath = "/tmp/" + timestr + "_" + computerName + "_syslog"
					if (osplatform == "Windows"):
						newpath = "C:\\temp\\"
						if not os.path.exists(newpath):
							os.makedirs(newpath)
						localpath = "C:\\temp\\" + timestr + "_" + computerName + "_syslog"
					else:
						localpath = "/tmp/" + timestr + "_" + computerName + "_syslog"	
					sftp.get(filepath,localpath)
				else:
					print("Error with SSH command", exit_status)
			print()
			print("Your system log can be found in : {}".format(localpath))
			runningSSH = False
			if sftp: sftp.close()
			if ssh: ssh.close()
		except paramiko.ssh_exception.NoValidConnectionsError as error:
			print(error)
			break
		except paramiko.ssh_exception.AuthenticationException as error:
			print(error)
			pass

networkscan()
runningSSH()