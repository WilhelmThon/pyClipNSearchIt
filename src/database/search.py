import ctypes
import collections
import datetime
import elasticsearch as es

from collections import defaultdict
from src import util
from src import logger
from .client import connect

def _generate_query(hash_):
    return {
        "function_score": {
            "query": {
                "constant_score": {
                    "boost": 0,
                    "filter": {
                        "bool": {
                            "should": [
                                { "term": { "fhash.f1": hash_[0:4] } },
                                { "term": { "fhash.f2": hash_[4:8] } },
                                { "term": { "fhash.f3": hash_[8:12] } },
                                { "term": { "fhash.f4": hash_[12:16] } },
                            ]
                        }
                    }
                }
            },
            "functions": [
                { 
                    "script_score": {
                        "script": {
                            "id": "hmd64bit",
                            "params": {
                                "field": "bhash",
                                # The subcode must be sent as a signed long to match the indexed long type
                                "subcode": ctypes.c_long(int(hash_, 16)).value
                            }
                        }
                    }
                }
            ],
            "boost_mode": "sum",
            "score_mode": "sum"
        }
    }

def _search_image(client: es.Elasticsearch, hash_: str):
    conf = util.get_config()["search"]
    results = []
    
    setting_max_size = conf["max_size_response"]
    setting_r = conf["r"]

    response = client.search(
        index="hashes", 
        size=setting_max_size,
        query=_generate_query(hash_),
        fields=[
            "origin",
            "hash",
            "timestamp"
        ],
        sort=[
            { 
                "_score": { "order": "asc" }
            }
        ],
        source=False
    )

    for hit in response["hits"]["hits"]:
        if hit["_score"] > setting_r:
            break

        results.append(hit)

    return results

def _search_video(client: es.Elasticsearch, data: dict):
    conf = util.get_config()["search"]
    results = []

    setting_max_size = conf["max_size_response"]
    setting_r = conf["r"]

    queries = []
    header = {
        "index": "hashes" 
    }

    for hash_ in data:
        queries.append(header)
        queries.append({
            "size": setting_max_size,
            "query": _generate_query(hash_),
            "fields": [
                "origin",
                "timestamp",
                "hash",
            ],
            "sort": [
                { 
                    "_score": { "order": "asc" }
                }
            ],
            "_source": False
        })

    responses = client.msearch(index=["hashes"], searches=queries, max_concurrent_searches=100)
    # Make results a dict first to ensure uniqueness of results
    results = {}

    for response in responses["responses"]:
        for hit in response["hits"]["hits"]:
            score = hit["_score"]

            if score > setting_r:
                break
            
            id_ = hit["_id"]
            existing_hit = results.get(id_, None)

            if (existing_hit is None) or (score < existing_hit["_score"]):
                results[id_] = hit

    # Convert results to a list
    results = list(results.values())
    # An insort would probably be better, but bisect doesn't support
    # keys before Python 3.10
    results.sort(key=lambda x: x["_score"])

    return results

def run(hash_sets: dict):
    client = connect()

    for origin in hash_sets:
        data = hash_sets[origin]
        searching_for_video = type(data) is dict

        try:
            # Image
            if not searching_for_video:
                results = _search_image(client, data)
            # Video
            else:
                results = _search_video(client, data)
        except Exception as e:
            logger.error(str(e))
            continue

        logger.info("---------------------------------------")
        logger.info(f"Search results for '{origin}':")

        if not results:
            logger.warning("No similar matches were found")
        else:
            match = results[0]
            match_fields = match["fields"]
            
            match_score = int(match["_score"])
            match_origin = match_fields["origin"][0]
            match_hash = match_fields["hash"][0]
            match_timestamp = match_fields.get("timestamp", None)

            additional_info = f" at the timestamp '{str(datetime.timedelta(seconds=match_timestamp[0]))}'" if match_timestamp else ""

            logger.info(f"The best single hash match '{match_hash}' was '{match_origin}',{additional_info} with a hemming distance score of '{match_score}'")
            
            if searching_for_video:
                if (match_hash in data) and data[match_hash] != match_timestamp[0]:
                    logger.info(f"Note that local timestamp '{str(datetime.timedelta(seconds=data[match_hash]))}' is not equal to the found timestamp '{str(datetime.timedelta(seconds=match_timestamp[0]))}', but that this is likely due to both frames originating from a image sequence in the video that is visually similar")

                if len(results) > 1:
                    best_origins = []
                    best_origins_timestamps = defaultdict(list)

                    for hit in results:
                        if int(hit["_score"]) != match_score:
                            break

                        match_fields = hit["fields"]
                        match_origin = match_fields["origin"][0]
                        match_timestamp = match_fields.get("timestamp", None)

                        if match_timestamp:  
                            best_origins_timestamps[match_origin].append(match_timestamp[0])

                        best_origins.append(match_origin)

                    # Count highest occurence and get seconds timestamps for those
                    best_origin, num_matches = collections.Counter(best_origins).most_common(1)[0]
                    best_origin_timestamps = best_origins_timestamps[best_origin]
                    
                    best_origin_timestamps.sort()

                    # Convert to string datetime timestamps
                    for i in range(0, len(best_origin_timestamps)):
                        best_origin_timestamps[i] = str(datetime.timedelta(seconds=best_origin_timestamps[i]))
                    
                    logger.info(f"The most likely origin is '{best_origin}' with '{num_matches}/{len(best_origins)}' of the best scored matches")
                    logger.info("The matched timestamps (in-order) were")
                    logger.info(best_origin_timestamps)