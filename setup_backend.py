import sys

from src import logger
from src import util

HMDSCRIPT_TEMPLATE = {
    "id": "hmd64bit",
    "script": {
        "lang": "painless",
        "source": """
            long u = params.subcode^doc[params.field].value;
            long uCount = u-((u>>>1)&-5270498306774157605L)-((u>>>2)&-7905747460161236407L);
            return ((uCount+(uCount>>>3))&8198552921648689607L)%63;
        """
    }
}

PIPELINE_TEMPLATE = {
    "id": "split-hash",
    "description": "Splits the input hashes into smaller subsets",
    "processors": [
        {
            "set": {
                "field": "fhash",
                "value": {}
            }
        },
        {
            "script" : {
                "lang": "painless",
                "source": """
                    ctx.bhash = new BigInteger(ctx.hash, 16).longValue();
                    ctx.fhash.f1 = ctx.hash.substring(0, 4);
                    ctx.fhash.f2 = ctx.hash.substring(4, 8);
                    ctx.fhash.f3 = ctx.hash.substring(8, 12);
                    ctx.fhash.f4 = ctx.hash.substring(12, 16);
                """
            }
        }
    ]
}

INDEX_TEMPLATE = {
    "index": "hashes",
    "settings" : {
        "number_of_shards": util.get_config()["elasticsearch_index"]["number_of_shards"],
        "number_of_replicas": util.get_config()["elasticsearch_index"]["number_of_replicas"],
        "default_pipeline": "split-hash"
    },
    "mappings": {
        "properties": {
            "origin": { "type": "text" },
            "timestamp": { "type": "integer" },
            "hash": { "type": "keyword" },
            "bhash": { "type": "long" },
            "fhash": {
                "properties": {
                    "f1": { "type": "keyword" },
                    "f2": { "type": "keyword" },
                    "f3": { "type": "keyword" },
                    "f4": { "type": "keyword" },
                }
            }
        }
    }
}

def clear(client):
    logger.info("...Attempting to delete old pipelines and indexes")
    try:
        client.indices.delete(index=INDEX_TEMPLATE["index"])
        client.ingest.delete_pipeline(id=PIPELINE_TEMPLATE["id"])
        client.delete_script(id=HMDSCRIPT_TEMPLATE["id"])
    except:
        pass
    logger.info("...Success, deleted old pipelines and indexes")

def setup(client):
    logger.info("...Attempting to create hemming distance script")
    client.put_script(**HMDSCRIPT_TEMPLATE)
    logger.info("...Success, created hemming distance script")

    logger.info("...Attempting to create split-hash pipeline")
    client.ingest.put_pipeline(**PIPELINE_TEMPLATE)
    logger.info("...Success, created split-hash pipeline")

    logger.info("...Attempting to create hash index")
    client.indices.create(**INDEX_TEMPLATE)
    logger.info("...Success, created hash index")

def main():
    logger.info("Running backend setup!")

    if not util.is_frontend_setup():
        logger.error("setup_frontend.py must be run first")
        return

    # Import later to not give error if frontend has not been ran
    import src.database as database

    try:
        client = database.connect()
    except Exception as e:
        logger.error(str(e))

    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        logger.info("Forcing clean setup")
        clear(client)
    
    if util.is_backend_setup(client):
        logger.error("The database is already setup")
        return

    setup(client)

    logger.info("Finished running backend setup!")

if __name__ == "__main__":
    main()