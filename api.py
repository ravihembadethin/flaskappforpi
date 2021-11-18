from netaddr import IPAddress
import requests, json
import subprocess
import os
from flask import Flask,flash, jsonify, redirect, request
from time import sleep

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
	print('We Are done Here! Rebooting System')
	sleep(1)
	subprocess.call('reboot')

@app.route('/network',methods=["GET","POST"])
def network():
	posted_data = request.get_json(force=True)
	print("GotData:",posted_data)

	ip_address = posted_data['ip_address']
	subnet= posted_data['subnet']
	gateway= posted_data['gateway']
	DCHP= posted_data['DCHP']
	interface= posted_data['interface']
	cidr=str(IPAddress(subnet).netmask_bits())

	line1='interface '+interface +'\n'
	line2='static ip_address='+ip_address+'/'+cidr+'\n' #SUBNET CIDR IS PENDING HERE
	line3='static routers='+ gateway +'\n'#HERE IS ROUTER ADDRESS IF YOUR ROUTER IS WORKING ON OTHER THAN GATEWAY IP
	line4='static domain_name_servers=8.8.8.8 fd51:42f8:caae:d92e::1'

	interface_down_cmd='sudo ip link set '+interface+' down'
	interface_up_cmd='sudo ip link set '+interface+' up'
	file_name_path="/etc/dhcpcd.conf"
	with open(file_name_path,'r') as dhc_conf_file:
		lines = dhc_conf_file.readlines()

	with open(file_name_path,'w') as dhc_conf_file:
		for line in lines:
			if line.find("interface") != -1:
				pass
			elif line.find("ip_address") != -1:
				pass
			elif line.find("static routers") != -1:
				pass
			elif line.find("static domain_name_servers") != -1:
				pass
			else:
				dhc_conf_file.write(line)
	with open(file_name_path, "a+") as dhc_conf_file:
		dhc_conf_file.seek(0)
		# If file is not empty then append '\n'
		data = dhc_conf_file.read(100)
		if len(data) > 0:
			dhc_conf_file.write(line1)
			dhc_conf_file.write(line2)
			dhc_conf_file.write(line3)
			dhc_conf_file.write(line4)
	os.popen(interface_down_cmd)
	os.popen(interface_up_cmd)
	return jsonify({'network': True}),200

if __name__=='__main__':
   app.run(debug=True, host='0.0.0.0', port=6006)
