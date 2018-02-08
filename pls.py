import json
from argparse import ArgumentParser
import os
import context
from colors import green

def log(message, tenant_id):
    print('\t...::[[ 🚿 ' + message + ' ' + green(tenant_id) + ' 🚿 ]]::...')

parser = ArgumentParser(description='PLS: Powerfull Lannister Script v2, manages applications.')

parser.add_argument('-c', '--config', help="Uses a specific config file (will be config.json by default).", default="config.json")

subparser = parser.add_subparsers(help="commands", dest="command")

add_parser = subparser.add_parser('add')
add_parser.add_argument('tenant')

del_parser = subparser.add_parser('remove')
del_parser.add_argument('tenant')

run_parser = subparser.add_parser('run')
run_parser.add_argument('tenants', nargs="+", type=str, help="Select the tenants to which we will perform the tasks (use 'all' to select all the tenants).")
run_parser.add_argument('-m', '--migrate', action="store_true", help="Migrate the databases.")
run_parser.add_argument('-r', '--restore', action="store_true", help="Restore the databases from the backups.")
run_parser.add_argument('-b', '--backup', action="store_true", help="Creates new backups from the databases.")
run_parser.add_argument('-a', '--all', action="store_true", help="Executes all tasks.")

args = parser.parse_args()
api = context.build()

if args.command == 'run':
    tenants = args.tenants
    if (len(args.tenants) == 1 and args.tenants[0] == 'all'):
        tenants = [tenant_id for tenant_id in api.config['tenants']]

    if args.restore or args.all:
        for tenant_id in tenants:
            log('restore', tenant_id)
            api.restore_tenant(tenant_id)
    if args.migrate or args.all:
        for tenant_id in tenants:
            log('migrate', tenant_id)
            api.migrate_tenant(tenant_id)
    if args.backup or args.all:
        for tenant_id in tenants:
            log('backup', tenant_id)
            api.backup_tenant(tenant_id)

elif args.command == 'remove':
    api = api.remove_tenant(args.tenant)
    api.save()

elif args.command == 'add':
    api = api.create_tenant(args.tenant)
    api.save()
