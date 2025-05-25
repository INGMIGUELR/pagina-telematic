from pymongo import MongoClient

# Conexión local a MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Base de datos y colección
db = client["mantenimientos"]
coleccion_registros = db["registros"]


