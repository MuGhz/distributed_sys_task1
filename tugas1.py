from flask import Flask,request,jsonify
from peewee import *
from models import *
import requests
import json

app = Flask(__name__)
database = SqliteDatabase('bank.db')

def get_quorum():
	#response = json.loads(requests.get('http://152.118.31.2/list.php').text)
	response = json.loads(requests.get('http://www.mocky.io/v2/59ddd7201000003e0ba84e8b').text)
	print (response)
get_quorum()

@app.before_request
def _db_connect():
	database.connect()

@app.teardown_request
def _db_close(exc):
	if not database.is_closed():
		database.close()

@app.route('/ewallet/ping',methods=['POST'])
def ping():
	return jsonify(pong=1),200

@app.route('/ewallet/register',methods=['POST'])
def register():
	try :
		nama = json.loads(request.data.decode("utf-8"))['nama']
		user_id = json.loads(request.data.decode("utf-8"))['user_id']
	except Exception as e:
		print (e)
		return jsonify(status_register="-99"),200
	try :
		nasabah, created = Nasabah.get_or_create(name=nama,npm=user_id)
	except Exception as e:
		print (e)
		return jsonify(status_register="4"),200
	return jsonify(status_register="1"),200

@app.route('/ewallet/getSaldo',methods=['POST'])
def getSaldo():
	try :
		user_id = json.loads(request.data.decode("utf-8"))['user_id']
	except Exception as e:
		print (e)
		return jsonify(nilai_saldo=-99),200
	try : 
		nasabah = Nasabah.get(npm=user_id)
	except Exception as e:
		print (e)
		return jsonify(nilai_saldo=-1),200
	try :
		saldo = nasabah.saldo
	except Exception as e:
		print (e)
		return jsonify(nilai_saldo=-4),200
	return jsonify(nilai_saldo=saldo),200