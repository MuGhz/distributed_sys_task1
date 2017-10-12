from flask import Flask,request,jsonify
from peewee import *
from models import *
import requests
import json,sys

app = Flask(__name__)
database = SqliteDatabase('bank.db')

def get_quorum():
	try :
		#response = json.loads(requests.get('http://152.118.31.2/list.php').text)
		response = json.loads(requests.get('http://www.mocky.io/v2/59ddd7201000003e0ba84e8b').text)
	except Exception as e:
		print (e)
	quorum = []
	for user in response :
		quorum.append(user['ip'])
	print (quorum)
	n = 0
	for ip in quorum :
		ip = 'http://'+ ip + '/ewallet/ping'
		ping = {}
		flag = True
		try :
			print ('ping....',ip)
			ping = json.loads(requests.post(ip,timeout=5).text)
		except Exception as e:
			flag = False
			print (e)
		if flag :
			try :
				if ping['pong'] == 1 :
					n += 1
					print ('pong.....')
			except (Exception,KeyError) as e :
				print ('ping not success in ',ip,' error :',e)
	vote = (n/(len(quorum))) * 100
	print ('hasil quorum :',vote)
	return vote

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
	vote = get_quorum()
	if vote < 50 :
		return jsonify(status_register=-2),200
	else :
		try :
			nama = json.loads(request.data.decode("utf-8"))['nama']
			user_id = json.loads(request.data.decode("utf-8"))['user_id']
		except Exception as e:
			print (e)
			return jsonify(status_register=-99),200
		try :
			Nasabah.create(name=nama,npm=user_id)
		except Exception as e:
			print (e)
			return jsonify(status_register=-4),200
		return jsonify(status_register=1),200

@app.route('/ewallet/getSaldo',methods=['POST'])
def getSaldo():
	vote = get_quorum()
	if vote < 50 :
		return jsonify(status_register=-2),200
	else :
		try :
			user_id = json.loads(request.data.decode("utf-8"))['user_id']
		except Exception as e:
			print (e)
			print ("error : ",sys.exc_info())
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

if __name__ == '__main__':
    app.run(threaded=True,port=80,host='0.0.0.0')
