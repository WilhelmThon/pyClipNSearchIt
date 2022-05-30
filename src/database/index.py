import multiprocessing as mp

from elasticsearch.helpers import parallel_bulk
from src import logger
from src import util
from .client import connect

def _generator(hash_sets: dict):
    for origin in hash_sets:
        data = hash_sets[origin]

        # Image
        if not type(data) is dict:
            yield {
                "_op_type": "create",
                "_index": "hashes",
                "_id": f"{origin[:16]}{data}",
                "_source": {
                    "origin": origin,
                    "hash": data,
                }
            }       
        # Video
        else:
            for hash_ in data:
                yield {
                    "_op_type": "create",
                    "_index": "hashes",
                    "_id": f"{origin[:16]}{hash_}",
                    "_source": {
                        "origin": origin,
                        "hash": hash_,
                        "timestamp": data[hash_]
                    }
                }

def _index(hash_sets: dict):
    client = connect()

    # For recommended settings see https://stackoverflow.com/questions/54962685/how-to-improve-parallel-bulk-from-python-code-for-elastic-insert
    for success, info in parallel_bulk(client, _generator(hash_sets), thread_count=8, chunk_size=10000, raise_on_error=False):
        if not success:
            reason = info["create"]["error"]["reason"]
            logger.info(reason)

def run(hash_sets: dict):
    with mp.Pool(processes=mp.cpu_count()) as pool:
        for _ in pool.imap_unordered(_index, util.dict_to_chunks(hash_sets, pool._processes)):
            pass