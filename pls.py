import json
from argparse import ArgumentParser
import os
import context
import requests
import decimal
import io
from config_api import ConfigApi

def configure_dbtask(sub):
    p = sub.add_parser('dbtask')
    p.add_argument('tenants', nargs="+", type=str, help="select the tenants to which we will perform the tasks (use 'all' to select all the tenants)")
    p.add_argument('-c', '--compile', action="store_true", help="compile the migrations projects from the solution before executing the migrations")
    p.add_argument('-m', '--migrate', action="store_true", help="migrate the databases")
    p.add_argument('-r', '--restore', action="store_true", help="restore the databases from the backups")
    p.add_argument('-b', '--backup', action="store_true", help="creates new backups from the databases")
    p.add_argument('-a', '--all', action="store_true", help="executes all tasks (this does not include the compilation step, use -ac if you want to do everything)")

def configure_config(sub):

    def add_common_config_args(parser):
        parser.add_argument('url', type=str, help="a configuration api url")
        parser.add_argument('-l', '--login', type=str, help="a valid login")
        parser.add_argument('-p', '--password', type=str, help="your password")

    def configure_export(sub):
        p = sub.add_parser('export')
        p.add_argument('-o', '--output-file', type=str, help="the file where the export will be saved")
        add_common_config_args(p)

    def configure_fixguid(sub):
        p = sub.add_parser('fixguid')
        add_common_config_args(p)

    p = sub.add_parser('config')
    sub = p.add_subparsers(help='config-commands', dest='config_command')

    configure_export(sub)
    configure_fixguid(sub)

def build_parser():
    parser = ArgumentParser(description='PLS: Powerfull Lannister Script v2, manages applications.')
    parser.add_argument('-c', '--config', help="Uses a specific config file (will be config.json by default).", default="config.json")

    sub = parser.add_subparsers(help='commands', dest='command')
    configure_dbtask(sub)
    configure_config(sub)

    return parser

def process(args):
    api = context.build(args.config or "config.json")

    if args.command == 'dbtask':
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

    elif args.command == 'config':
        config_api = ConfigApi(args.url, args.login, args.password)

        if args.config_command == 'export':
            config_api.get_config(args.output_file)

        elif args.config_command == 'fixguid':
            config_api.fixguid()

parser = build_parser()
args = parser.parse_args()

process(args)
