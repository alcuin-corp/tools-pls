import json
import argparse
import os

argparser = argparse.ArgumentParser()

argparser.add_argument('-c', '--config', default='config.json')
argparser.add_argument('-r', '--remove', action="store_true")
argparser.add_argument('-a', '--add', action="store_true")
argparser.add_argument('tenant_name')

args = argparser.parse_args()

if not (os.path.exists(args.config)):
    print("Can't load config file.")
    exit()

f = open(args.config, 'r')
config = json.load(f)
f.close()

print(config["tenants"])

if args.remove:
    config["tenants"] = [t for t in config["tenants"] if t["name"] != args.tenant_name]

if args.add:
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

f = open(args.config, 'w')
f.write(json.dumps(config))
f.flush()
