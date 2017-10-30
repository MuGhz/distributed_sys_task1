import cmd,json,requests
from peewee import *
from models import *

database = SqliteDatabase('bank.db')

class Interface(cmd.Cmd) :
	
	def do_saldo(self, line):
		arg = line.split(" ")
		ip = arg[0]
		user_id = arg[1]
		input = {}
		input['user_id']=user_id
		input = json.dumps(input)
		ip = "http://" + ip + "/ewallet/getSaldo"
		try :
			response = json.loads(requests.post(ip, data = input).text)
			print (response)
		except Exception as e:
			print (e)
		try :
			if response['nilai_saldo'] == -1 :
				print ('nasabah belum terdaftar, silahkan melakukan register')
			elif response['nilai_saldo'] == -2 :
				print ('quorum belum terpenuhi')
			elif response['nilai_saldo'] == -4 :
				print ('database error')
			elif response['nilai_saldo'] == -99 :
				print('kesalahan-belum terdefinisi')
		except KeyError as k :
			print ("keyerror ",k)

	def do_register(self,line):
		arg = line.split(" ")
		ip = arg[0]
		nama = arg[1]
		user_id = arg[2]
		ip = "http://" + ip + "/ewallet/register"
		input ={}
		input['user_id']=user_id
		input['nama']=nama
		input=json.dumps(input)
		try :
			response = json.loads(requests.post(ip, data = input).text)
			print (response)
		except Exception as e:
			print (e)
		try :
			if response['status_register'] == -2 :
				print ('quorum tidak terpenuhi')
			elif response['status_register'] == -4 :
				print ('database error')
			elif response['status_register'] == -99 :
				print ('kesalahan-belum terdefinisi')
		except KeyError as k :
			print ('keyerror :',k)
	
	def do_ping(self,line):
		ip='http://'+line+'/ewallet/ping'
		try :
			response=json.loads(requests.post(ip).text)
			print (response)
			if response['pong']==1:
				print ("ping success")
		except (Exception,KeyError) as e :
			print ('error :', e)
	def do_transfer(self,line):
		arg = line.split(" ")
		api = "http://" + arg[0] + "/ewallet/transfer"
		user_id = arg[1]
		nominal = int(arg[2])
		input = {"user_id":user_id,"nilai":nominal}
		input = json.dumps(input)
		try :
			response = json.loads(requests.post(api, data = input).text)
			print (response)
		except Exception as e:
			print (e)
		try :
			if response['status_transfer'] == 1 :
				transfer_success(user_id,nominal)
				print ('Transfer sukses')
			elif response['status_transfer'] == -2 :
				print ('quorum tidak terpenuhi')
			elif response['status_transfer'] == -1 :
				print ('user_id belum terdaftar')
			elif response['status_transfer'] == -4 :
				print ('kesalahan database')
			elif response['status_transfer'] == -5 :
				print ('nilai transfer diluar ketentuan')
			elif response['status_transfer'] == -99 :
				print ('kesalahan belum terdefinisi')
		except (Exception,KeyError) as e:
			print ('error :',e)

	def transfer_success(user_id,nominal):
		database.connect()
		try :
			nasabah = Nasabah.get(npm=user_id)
			nasabah.saldo -= nominal
			print ("saldo anda : ",nasabah.saldo)
			nasabah.save()
		except Exception as e:
			print (e)
		database.close()

	def do_simpan(self,line):
		arg = line.split(" ")
		user_id = arg[0]
		nominal = int(arg[1])
		database.connect()
		try :
			nasabah = Nasabah.get(npm=user_id)
			nasabah.saldo += nominal
			nasabah.save()
			print ("berhasil menambahkan saldo, saldo anda : ", nasabah.saldo)
		except Exception as e:
			print (e)

	def do_totalSaldo(self,line):
		arg = line.split(" ")
		api = "http://" + arg[0] + "/ewallet/getTotalSaldo"
		user_id = arg[1]
		input = {"user_id":user_id}
		input = json.dumps(input)
		try :
			response = json.loads(requests.post(api, data = input).text)
		except Exception as e:
			print (e)
		try :
			if response['nilai_saldo'] == -2 :
				print ('quorum tidak terpenuhi')
			elif response['nilai_saldo'] == -1 :
				print ('user_id belum terdaftar')
			elif response['nilai_saldo'] == -3 :
				print ('pemanggilan host tidak berhasil')
			elif response['nilai_saldo'] == -99 :
				print ('kesalahan belum terdefinisi')
			else :
				print ('saldo anda ',response['nilai_saldo'])
		except (Exception,KeyError) as e:
			print ('error :',e)

	def do_EOF(self, line):
		return True

if __name__ == '__main__':
	print ('<<<<<<<<<<<<<<<<<<<<<<<<<E-WALLET>>>>>>>>>>>>>>>>>>>>>>>>>')
	print ('==========================================================')
	print ('PETUNJUK :')
	print ('untuk registrasi = register <IP> <NAMA> <USER_ID>')
	print ('untuk cek saldo = saldo <IP> <USER_ID>')
	print ('untuk ping = ping <IP>')
	print ('untuk transfer = transfer <IP> <USER_ID> <NOMINAL>')
	print ('untuk menambahkan saldo = simpan <USER_ID> <NOMINAL>')
	print ('untuk mendapatkan total saldo = totalSaldo <IP> <USER_ID>')
	print ('==========================================================')
	Interface().cmdloop()
