import src.logger as logger
import src.util as util
import src.arguments as arguments
import src.database as database
import src.hasher as hasher

from src.structures import MenuOptions

def main():
    if not util.is_frontend_setup():
        logger.error("Run setup_frontend.py first!")
        return

    args = arguments.parse()

    try:
        if args.option == MenuOptions.STATISTICS:
            database.print_statistics()
        else:
            hash_sets = hasher.run(args)

            if args.option == MenuOptions.INDEX:
                database.index_hashes(hash_sets)
            elif args.option == MenuOptions.SEARCH:
                database.search_hashes(hash_sets)

    except Exception as e:
        logger.error(str(e))

if __name__ == "__main__":
    main()