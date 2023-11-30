from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import sys
import datetime
import os

def procesar_json(ruta_json, repo_name):
    with open(ruta_json, 'r') as file:
        data = json.load(file)

    puntos = []
    for dependencia in data.get('dependencies', []):
        if dependencia.get('vulnerabilities'):
            for vulnerabilidad in dependencia['vulnerabilities']:
                punto = Point("vulnerabilidades") \
                    .tag("repository", repo_name) \
                    .tag("fileaffected", dependencia.get('fileName')) \
                    .tag("cve", vulnerabilidad.get('name')) \
                    .field("severity", vulnerabilidad.get('severity')) \
                    .field("cvssScore", vulnerabilidad.get('cvssv3', {}).get('baseScore', 0)) \
                    .field("hasVulnerabilities", True) \
                    .time(datetime.datetime.utcnow(), WritePrecision.NS)
                puntos.append(punto)
        else:
            # Crear un punto para dependencias sin vulnerabilidades
            punto = Point("vulnerabilidades") \
                .tag("repository", repo_name) \
                .tag("fileaffected", dependencia.get('fileName')) \
                .field("hasVulnerabilities", False) \
                .time(datetime.datetime.utcnow(), WritePrecision.NS)
            puntos.append(punto)
    return puntos

def enviar_a_influxdb(puntos):
    token = os.getenv('INFLUXDB_TOKEN')  # Lee el token desde la variable de entorno
    org = 'vodafone'  # Tu organización
    bucket = 'vodafone'  # Tu bucket
    url = 'http://influxdb-service.dependency-check-devsecops-ns.svc.cluster.local:8086'

    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)  # Modificado para usar opciones sincrónicas

    result = write_api.write(bucket=bucket, record=puntos)
    print(str(result))
    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: script.py <ruta_del_json> <nombre_del_repositorio>")
        sys.exit(1)

    ruta_json = sys.argv[1]
    nombre_repositorio = sys.argv[2]
    puntos = procesar_json(ruta_json, nombre_repositorio)
    print(str(puntos))
    enviar_a_influxdb(puntos)
