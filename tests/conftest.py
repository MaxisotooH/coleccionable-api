import os

# Fuerza sin Mongo real en tests (pisa .env; prioridad sobre el archivo)
os.environ["MONGODB_URI"] = ""
os.environ["MONGODB_DB_NAME"] = "test_tienda"
