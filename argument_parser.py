import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='Combine chart entries in to songs')
    parser.add_argument(
        '-s',
        '--seed',
        action="store_true",
        help=
        "Elasticsearch - Add existing songs to elasticsearch (bootstrap/seed)")
    parser.add_argument('-c',
                        '--continue_songs',
                        action="store_true",
                        help="Continue adding songs (works with -n)")
    parser.add_argument(
        '-m',
        '--merge',
        action='store_true',
        help='Check if entries with a potential match should be combined')
    parser.add_argument(
        '--user-input-disabled',
        action='store_true',
        help=
        'For use with merge, disable user input and leave questionable songs untouched',
        dest='user_input_disabled')
    parser.add_argument('-f',
                        '--force-create-rest',
                        action='store_true',
                        help='Create new songs for questionable songs',
                        dest='force_create')
    parser.add_argument('-n',
                        '--number',
                        type=int,
                        help="The number of items to work on, -1 for all",
                        default=-2)
    parser.add_argument('-t',
                        '--tier',
                        action='store_true',
                        help='Create tiered songs',
                        dest='tier')
    parser.add_argument('-e',
                        '--elastic',
                        action='store_true',
                        help='Create known uniques with elastic search',
                        dest='elastic_tier')
    parser.add_argument('-w',
                        '--wait',
                        type=int,
                        help="Wait for the db to be available for n seconds")
    parser.add_argument('--copy',
                        nargs=2,
                        help='Copy from one db to another (mysql, sqlite)')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    print(get_args())
