__all__ = ('client', 'index', 'search')
from src import logger

from .client import *
from . import index
from . import search

def print_statistics():
    client = connect()

    client.indices.refresh(index="hashes")
    
    res = client.nodes.info()
    cluster_name = res["cluster_name"]
    nodes_total = res["_nodes"]["total"]
    nodes_up = res["_nodes"]["successful"]
    nodes_info = []
    
    for node in res["nodes"].values():
        node_name = node["name"]
        node_roles = ', '.join(node["roles"])
        node_bytes = node["jvm"]["mem"]["heap_init_in_bytes"]
        nodes_info.append(f"Node '{node_name}', Roles ({node_roles}), Heap size init '{node_bytes}' B")

    res = client.count(index="hashes")
    docs_count = res["count"]

    logger.info(f"Cluster '{cluster_name}', Nodes Up ({nodes_up}/{nodes_total})")
    for info in nodes_info:
        logger.info(info)
    logger.info(f"Number of documents (hashed images) in Index 'hashes': {docs_count}")

def index_hashes(hash_sets: dict):
    logger.info("Indexing hashes, please wait...")
    index.run(hash_sets)
    logger.info("Finished indexing hashes!")

def search_hashes(hash_sets: dict):
    logger.info("Searching for matches, please wait...")
    search.run(hash_sets)
    logger.info("Finished search!")