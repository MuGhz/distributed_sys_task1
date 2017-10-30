import cmd,json,requests
from peewee import *
from models import *

database = SqliteDatabase('bank.db')
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

class Interface(cmd.Cmd) :
	intro = 'Selamat datang di e-wallet cabang 1406559055.\nDaftar perintah : saldo, register, ping, transfer, totalSaldo, simpan, ambil, dan quit.\nUntuk bantuan ketik help atau ? \n'
	prompt = '(e-wallet)'

	def do_saldo(self, line):
		'untuk mengecek saldo nasabah = saldo <IP> <USER_ID>'
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
		'untuk registrasi nasabah pada bank = register <IP> <NAMA> <USER_ID>'
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
		'untuk ping kantor cabang bang lain = ping <IP>'
		ip='http://'+line+'/ewallet/ping'
		try :
			response=json.loads(requests.post(ip).text)
			print (response)
			if response['pong']==1:
				print ("ping success")
		except (Exception,KeyError) as e :
			print ('error :', e)

	def do_transfer(self,line):
		'untuk melakukan transfer saldo nasabah = transfer <IP> <USER_ID> <NOMINAL>'
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

	def do_simpan(self,line):
		'untuk menambahkan saldo nasabah = simpan <USER_ID> <NOMINAL>'
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
		database.close()

	def do_ambil(self,line):
		'untuk mengambil uang dari bank(mengurangi saldo) nasabah = ambil <USER_ID> <NOMINAL>'
		arg = line.split(" ")
		user_id = arg[0]
		nominal = int(arg[1])
		database.connect()
		try :
			nasabah = Nasabah.get(npm=user_id)
			nasabah.saldo -= nominal
			nasabah.save()
			print ("berhasil mengambil uang, saldo anda :", nasabah.saldo)
		except Exception as e:
			print (e)
		database.close()

	def do_totalSaldo(self,line):
		'untuk mendapatkan total saldo nasabah = totalSaldo <IP> <USER_ID>'
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

	def do_quit(self, line):
		'untuk keluar dari e-wallet'
		print ('Terima kasih telah menggunakan layanan e-wallet')
		return True

if __name__ == '__main__':
	print ('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<E-WALLET>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
	print ('==============================================================================')
	Interface().cmdloop()
