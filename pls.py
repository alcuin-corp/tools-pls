import json
from argparse import ArgumentParser
import os
import context
import requests
import io
from config_api import ConfigApi

def build_parser():
    parser = ArgumentParser(description='PLS: Powerfull Lannister Script v2, manages applications.')

    parser.add_argument('-c', '--config', help="Uses a specific config file (will be config.json by default).", default="config.json")

    subparser = parser.add_subparsers(help="commands", dest="command")

    def add_config_api_args(target):
        target.add_argument('url', type=str, help="a configuration api url")
        target.add_argument('-l', '--login', type=str, help="a valid login")
        target.add_argument('-p', '--password', type=str, help="your password")

    export_parser = subparser.add_parser('export')
    add_config_api_args(export_parser)
    export_parser.add_argument('-o', '--output-file', type=str, help="the file where the export will be saved")

    import_parser = subparser.add_parser('import')
    add_config_api_args(import_parser)

    add_parser = subparser.add_parser('add')
    add_parser.add_argument('tenant')

    del_parser = subparser.add_parser('remove')
    del_parser.add_argument('tenant')

    run_parser = subparser.add_parser('run')
    run_parser.add_argument('tenants', nargs="+", type=str, help="select the tenants to which we will perform the tasks (use 'all' to select all the tenants)")
    run_parser.add_argument('-c', '--compile', action="store_true", help="compile the migrations projects from the solution before executing the migrations")
    run_parser.add_argument('-m', '--migrate', action="store_true", help="migrate the databases")
    run_parser.add_argument('-r', '--restore', action="store_true", help="restore the databases from the backups")
    run_parser.add_argument('-b', '--backup', action="store_true", help="creates new backups from the databases")
    run_parser.add_argument('-a', '--all', action="store_true", help="executes all tasks (this does not include the compilation step, use -ac if you want to do everything)")

    return parser

def process(args):
    api = context.build(args.config or "config.json")
    
    if args.command == 'run':
        tenants = args.tenants
        if (len(args.tenants) == 1 and args.tenants[0] == 'all'):
            tenants = [tenant_id for tenant_id in api.config['tenants']]

        if args.compile:
            api.compile_migrations()

        if args.restore or args.all:
            api.restore_tenants(*tenants)
        if args.migrate or args.all:
            api.migrate_tenants(*tenants)
        if args.backup or args.all:
            api.backup_tenants(*tenants)

    elif args.command == 'export':
        config_api = ConfigApi(args.url, args.login, args.password)
        config_api.get_config(args.output_file)

    elif args.command == 'remove':
        api = api.remove_tenant(args.tenant)
        api.save()

    elif args.command == 'add':
        api = api.create_tenant(args.tenant)
        api.save()
    
parser = build_parser()
args = parser.parse_args()

process(args)
