from peewee import *

sqlite_db = SqliteDatabase('/root/tugas1/bank.db')

class BaseModel(Model):
	class Meta:
		database = sqlite_db

class Nasabah(BaseModel):
	name = CharField()
	npm = CharField(unique=True)
	saldo = DoubleField(default=0)

def create_tables():
	sqlite_db.connect()
	sqlite_db.create_tables([Nasabah])

if __name__ == "__main__":
	create_tables()
