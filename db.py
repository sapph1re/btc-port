from peewee import Model, CharField, IntegerField, BooleanField, DecimalField, IntegrityError
from playhouse.db_url import connect
from dotenv import load_dotenv
import os


load_dotenv()
db = connect(os.getenv('DB_URL'))


class BaseModel(Model):
    class Meta:
        database = db


class Transaction(BaseModel):
    asset = CharField(max_length=32)
    txid = CharField(max_length=64, unique=True)
    user_address = CharField(max_length=64)
    amount = DecimalField(max_digits=20, decimal_places=10)
    is_incoming = BooleanField()
    block = IntegerField()


# Create tables if they don't exist
db.create_tables([
    Transaction, 
], safe=True)
print("Database tables are in place")
