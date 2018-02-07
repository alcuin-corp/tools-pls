import json
from argparse import ArgumentParser
import os
import api

def load_config_file(config_file):
    if not (os.path.exists(config_file)):
        print("Can't load config file.")
        exit()

    f = open(config_file, 'r')
    config = json.load(f)
    f.close()
    return config

def save_config_file(config, config_file):
    f = open(config_file, 'w')
    f.write(json.dumps(config, sort_keys=True, indent=4))
    f.flush()

parser = ArgumentParser(description='PLS: Powerfull Lannister Script v2, manages applications.')

parser.add_argument('-c', '--config', help="Uses a specific config file (will be config.json by default).", default="config.json")

subparser = parser.add_subparsers(help="commands", dest="command")

add_parser = subparser.add_parser('add')
add_parser.add_argument('tenant_name')

del_parser = subparser.add_parser('remove')
del_parser.add_argument('tenant_name')

run_parser = subparser.add_parser('run')
run_parser.add_argument('-m', '--migrate', action="store_true", help="Migrate the databases.")
run_parser.add_argument('-r', '--restore', action="store_true", help="Restore the databases from the backups.")
run_parser.add_argument('-b', '--backup', action="store_true", help="Creates new backups from the databases.")
run_parser.add_argument('-a', '--all', action="store_true", help="Executes all tasks.")

args = parser.parse_args()

config = load_config_file(args.config)

if args.command == 'run':
    api = api.Api(config)
    if args.restore or args.all:
        api.restore()
    if args.migrate or args.all:
        api.migrate()
    if args.backup or args.all:
        api.backup()   

elif args.command == 'remove':
    config["tenants"] = [t for t in config["tenants"] if t["name"] != args.tenant_name]
    save_config_file(config, args.config)

elif args.command == 'add':
    config["tenants"].append({
        "name": args.tenant_name,
        "public": {
            "db": args.tenant_name,
            "backup": args.tenant_name + '.bak',
        },
        "config": {
            "db": args.tenant_name + "_ADM",
            "backup": args.tenant_name + '_ADM.bak',
        },
    })
    save_config_file(config, args.config)

