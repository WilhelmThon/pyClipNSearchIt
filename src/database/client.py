import elasticsearch as es

from src import util

def _is_connected(client: es.Elasticsearch):
    connected = False

    try:
        connected = client.ping()
    except:
        pass

    return connected

def connect():
    conf = util.get_config()["elasticsearch"]
    client = es.Elasticsearch(**conf)

    if not _is_connected(client):
        raise Exception("Could not connect to the elasticsearch database")

    return client