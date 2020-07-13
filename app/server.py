import os
import datetime
import rfc3339

from flask import Flask, request, jsonify
from influxdb import InfluxDBClient

app = Flask(__name__)

client=InfluxDBClient(host='db', port=8086, username='pinger', password='secretpassword')
client.create_database('pinger')
client.switch_database('pinger')

# returns set
def get_hosts():
	try:
		with open('hosts', 'r') as f:
			hosts=f.read().splitlines()
	except:
		hosts=[]
	return set(hosts)

def set_hosts(hosts):
	# TODO race
	with open('hosts', 'w') as f:
		for item in hosts:
			f.write("%s\n" % item)


@app.route('/hosts')
def hostlist():
	hosts = list(get_hosts())
	return "\n".join(hosts)

@app.route('/register')
def add_host():
	ip = request.remote_addr
	h = get_hosts()
	h.add(ip)
	set_hosts(h)
	return ip

@app.route('/remove/<ip>')
def remove_host(ip):
	h=get_hosts()
	h.discard(ip)
	set_hosts(h)
	return ip

@app.route('/test', methods=['POST',])
def store_test():
	source = request.remote_addr
	tests = request.get_json()
	dtnow = rfc3339.rfc3339(datetime.datetime.now(), utc=True)
	points = []
	for dst in tests:
		if dst == '0.0.0.0':
			continue
		points.append({
			"measurement": "ping",
			"tags": {
				"src": source,
				"dst": dst
			},
			"time": dtnow,
			"fields": {
				"result": tests[dst]
			}
		})

	client.write_points(points)
	client.close()
	return jsonify(points)
