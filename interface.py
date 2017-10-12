import cmd,json,requests

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

	def do_EOF(self, line):
		return True

if __name__ == '__main__':
	Interface().cmdloop()
