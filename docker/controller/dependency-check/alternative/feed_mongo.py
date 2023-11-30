import pymongo
import json
import sys
import datetime

def procesar_json(ruta_json, repo_name):
    # Procesar el archivo JSON
    with open(ruta_json, 'r') as file:
        data = json.load(file)

    # Añadir metadatos adicionales
    data['timestamp'] = datetime.datetime.utcnow().isoformat()
    data['repository'] = repo_name

    return data

def enviar_a_mongo(data):
    # Conexión a MongoDB
    client = pymongo.MongoClient("mongodb-service.dependency-check-devsecops-ns.svc.cluster.local:27017")
    db = client["dependency-check"]
    coleccion = db["main-analysis"]

    # Insertar datos
    coleccion.insert_one(data)

    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: script.py <ruta_del_json> <nombre_del_repositorio>")
        sys.exit(1)

    ruta_json = sys.argv[1]
    nombre_repositorio = sys.argv[2]
    data = procesar_json(ruta_json, nombre_repositorio)
    enviar_a_mongo(data)