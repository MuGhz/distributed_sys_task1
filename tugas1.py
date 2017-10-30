from flask import Flask,request,jsonify
from peewee import *
from models import *
import requests
import json,sys,socket

app = Flask(__name__)
database = SqliteDatabase('bank.db')
hostname = socket.gethostbyname(socket.gethostname())

def get_quorum():
	try :
		#response = json.loads(requests.get('http://152.118.31.2/list.php').text)
		response = json.loads(requests.get('http://www.mocky.io/v2/59df65fa0f00001009173c3f').text)
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
	print ('Hasil quorum :',vote)
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
		return jsonify(nilai_saldo=-2),200
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

@app.route('/ewallet/transfer',methods=['POST'])
def transfer():
	vote = get_quorum()
	if vote < 50 :
		return jsonify(status_transfer=-2),200
	else :
		try :
                        user_id = json.loads(request.data.decode("utf-8"))['user_id']
		except Exception as e:
                        print ("error : ",sys.exc_info())
                        return jsonify(status_transfer=-99),200
		try :
                        nasabah = Nasabah.get(npm=user_id)
		except Exception as e:
                        print (e)
                        return jsonify(status_transfer=-1),200
		try :
			nominal = json.loads(request.data.decode("utf-8"))["nilai"]
			nominal = int(nominal)
		except Exception as e:
			print (e)
			return jsonify(status_transfer=-99),200
		if nominal < 0 or nominal > 1000000000 :
			return jsonify(status_transfer=-5),200
		try :
			nasabah.saldo += nominal
			nasabh.save()
			return jsonify(status_transfer=1),200
		except Exception as e:
			print (e)
			return jsonify(status_transfer=-4),200

def get_cabang():
	try :
                #response = json.loads(requests.get('http://152.118.31.2/list.php').text)
                response = json.loads(requests.get('http://www.mocky.io/v2/59df65fa0f00001009173c3f').text)
	except Exception as e:
                print (e)
	cabang = {}
	for user in response :
		ip=user['ip']
		user_id=user['npm']
		cabang[user_id]=ip
	return cabang

def cek_cabang(id):
        cabang = get_cabang()
        if cabang[id] is hostname:
                return 1
        else :
                return 0

@app.route('/ewallet/getTotalSaldo',methods=['POST'])
def getTotalSaldo():
	vote = get_quorum()
	if vote is not 100:
		return jsonify(nilai_saldo=-2),200
	else:	
		try :
                        user_id = json.loads(request.data.decode("utf-8"))['user_id']
		except Exception as e:
                        print ("error : ",sys.exc_info())
                        return jsonify(nilai_saldo=-99),200
		try :
                        nasabah = Nasabah.get(npm=user_id)
		except Exception as e:
                        print (e)
                        return jsonify(status_transfer=-1),200
		cabang = get_cabang()
		if cek_cabang(user_id) is 0 :
			request_total = 'http://' + cabang[user_id] + '/ewallet/getTotalSaldo'
			try :
				post_data={"user_id":user_id}
				post_data=json.dumps(post_data)
				total_saldo = json.loads(requests.post(request_total, data = post_data).text)
			except Exception as e:
				print (e)
				return jsonify(nilai_saldo=-99),200
			return jsonify(nilai_saldo=total_saldo['nilai_saldo']),200
		else :
			sum = 0.0
			for bank in cabang :
				api = 'http://' + bank['ip'] + '/ewallet/getSaldo'
				post_data = {"user_id":user_id}
				post_data = json.dumps(post_data)
				try :
					saldo = json.loads(requests.post(api,data = post_data).text)
				except Exception as e: 
					print (e)
					return jsonify(nilai_saldo=-3),200
				if saldo['nilai_saldo'] > 0 :
					sum += saldo['nilai_saldo']
			return jsonify(nilai_saldo=sum),200

if __name__ == '__main__':
    app.run(threaded=True,port=80,host='0.0.0.0')
