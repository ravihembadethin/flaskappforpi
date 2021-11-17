# flaskappforpi
1.sudo apt-get install python3
2.sudo apt-get install python3-pip -y
3.pip3 install -r requirements.txt
4.python3 api.py

curl --location --request POST 'http://IP_AddressofPi:6006/network' \
--header 'Content-Type: application/json' \
--data-raw '{
"ip_address": "192.168.0.15",
"interface": "eth0",
"subnet": "255.255.254.0",
"gateway": "192.168.1.1",
"DCHP": "True"
} '