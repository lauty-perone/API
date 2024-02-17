from pymongo import MongoClient

#Base de datos remota
db_client = MongoClient(
    "mongodb+srv://lauty:lauty@cluster0.61lfmy8.mongodb.net/?retryWrites=true&w=majority").pruebas

#Base de datos local
#db_client = MongoClient().local
