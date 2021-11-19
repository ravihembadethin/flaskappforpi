from netaddr import IPAddress
import requests, json
import subprocess
import os
from flask import Flask,flash, jsonify, redirect, request
from time import sleep
import re

app= Flask(__name__)

@app.route("/", methods=["GET"])
def index():
	# return.redirect("/index.html");
	return jsonify({'index': True}),200


@app.route('/online',methods=["GET"])
def online():
	return jsonify({'online': True}),200


@app.route('/devices',methods=["POST"])
def devices():
	print(req.body);
	return jsonify({'devices': True}),200

@app.route('/reboot',methods=["GET","POST"])
def reboot():
	print('Rebooting System')
	sleep(1)
	subprocess.call('reboot')

@app.route('/network',methods=["GET","POST"])
def network():
	response={}
	file_name_path="/etc/dhcpcd.conf"
	if request.method == 'POST':
		response["valid_gw"]=""
		response["valid_ip"]=""
		response["valid_subnet"]=""
		response["valid_inteface"]=""
		response["valid_dhcp"]=""

		posted_data=request.get_json(force=True)
		print("GotData:",posted_data)
		ip_address=posted_data['ip_address']
		subnet= posted_data['subnet']
		gateway= posted_data['gateway']
		dhcp= posted_data['dhcp']
		interface= posted_data['interface']
		cidr=''

		response["valid_dhcp"]="" if dhcp in [True,False] else "Need boolean value in dhcp"
		if dhcp != True:
			status=os.system('sudo systemctl stop dhcpcd.service')
			response["dhcp_service"]="DHCP service stopped"

		else:
			status=os.system('sudo systemctl start dhcpcd.service')
			response["dhcp_service"]="DHCP service started"

		ip_regex="^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
		gateway_regex="^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

		subnet_regex="^(((255.){3}(255|254|252|248|240|224|192|128|0+))|((255.){2}(255|254|252|248|240|224|192|128|0+).0)|((255.)(255|254|252|248|240|224|192|128|0+)(.0+){2})|((255|254|252|248|240|224|192|128|0+)(.0+){3}))$"
		# valid_inteface=interface in ['eth0','eth1']

		response["valid_inteface"]="" if interface in ['eth0','eth1'] else "Invalid interface value"

		if not (re.search(ip_regex, ip_address)):
			response["valid_ip"]="Invalid Ip address value"

		if not (re.search(gateway_regex, gateway)):
			response["valid_gw"] =" Invalid Ip address value"

		if not (re.search(subnet_regex, subnet)):
			response["valid_subnet"]="Invalid subnet address value"

		if response['valid_inteface'] or response['valid_gw'] or response['valid_ip'] or response['valid_dhcp'] or response['valid_subnet']:
			response["network"]= "false"
			return jsonify(response),400
			
		cidr=str(IPAddress(subnet).netmask_bits())
		line1='interface '+interface +'#'+interface+'\n'
		line2='static ip_address='+ip_address+'/'+cidr+'#'+interface +'\n' #SUBNET CIDR IS PENDING HERE
		line3='static routers='+ gateway +'#'+interface+'\n'
		line4='static domain_name_servers=8.8.8.8 fd51:42f8:caae:d92e::1' +'#'+interface +'\n'

		interface_down_cmd='sudo ip link set '+interface+' down'
		interface_up_cmd='sudo ip link set '+interface+' up'
		with open(file_name_path,'r') as dhc_conf_file:
			lines=dhc_conf_file.readlines()

		with open(file_name_path,'w') as dhc_conf_file:
			for line in lines:
				tmp='#'+interface
				if line.find(tmp) != -1:
					if line.find(line1) != -1:
						pass
					elif line.find("ip_address") != -1:
						pass
					elif line.find("static routers") != -1:
						pass
					elif line.find("static domain_name_servers") != -1:
						pass
					else:
						dhc_conf_file.write(line)
				else:
					dhc_conf_file.write(line)
		with open(file_name_path, "a+") as dhc_conf_file:
			dhc_conf_file.seek(0)
			# If file is not empty then append '\n'
			data=dhc_conf_file.read(100)
			if len(data) > 0:
				dhc_conf_file.write(line1)
				dhc_conf_file.write(line2)
				dhc_conf_file.write(line3)
				dhc_conf_file.write(line4)
		# os.popen(interface_down_cmd)
		# os.popen(interface_up_cmd)
			return jsonify(response),400
	elif request.method == 'GET':
		response={}
		network={}
		eth0={}
		eth1={}
		eth0["dhcp"]=False
		eth1["dhcp"]=False
		x='#eth0'
		y='#eth1'
		status=os.system('sudo systemctl is-active --quiet dhcpcd.service')
		if(status == 0):
			eth1["dhcp"]=True
			eth0["dhcp"]=True
		with open (file_name_path,"r") as f:
			for line in f:
				if '#'!= line[0]:
					# print(line)
					if x in line:
						# print(line)
						if "static ip_address" in line:
							cidr_ar=line.split("/")
							cidr=cidr_ar[1].split("#")
							ip_address=cidr_ar[0].split("=")
							subnet='.'.join([str((m>>(3-i)*8)&0xff) for i,m in enumerate([-1<<(32-int(cidr[0]))]*4)])
							eth0['ip_address']=ip_address[1]
							eth0['subnet']=subnet
						elif "static routers" in line:
							gateway=line.split("=")
							gateway=gateway[1].split("#")
							eth0["gateway"]=gateway[0]

					elif y in line:
						# print(line)
						if "static ip_address" in line:
							cidr_ar=line.split("/")
							cidr=cidr_ar[1].split("#")
							ip_address=cidr_ar[0].split("=")
							subnet='.'.join([str((m>>(3-i)*8)&0xff) for i,m in enumerate([-1<<(32-int(cidr[0]))]*4)])
							eth1['ip_address']=ip_address[1]
							eth1['subnet']=subnet
						elif "static routers" in line:
							gateway=line.split("=")
							gateway=gateway[1].split("#")
							eth1["gateway"]=gateway[0]
		network['eth1']=eth1
		network['eth0']=eth0
		response['network']=network
	return jsonify(response),200

if __name__=='__main__':
   app.run(debug=True, host='0.0.0.0', port=6006)
