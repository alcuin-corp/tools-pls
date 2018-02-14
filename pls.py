from argparse import ArgumentParser

import context
from config_api import ConfigApi


def configure_dbtask(sub):
    p = sub.add_parser('dbtask')
    p.add_argument('tenants', nargs="+", type=str, help="select the tenants to which we will perform the tasks (use "
                                                        "'all' to select all the tenants)")
    p.add_argument('-c', '--compile', action="store_true", help="compile the migrations projects from the solution "
                                                                "before executing the migrations")
    p.add_argument('-m', '--migrate', action="store_true", help="migrate the databases")
    p.add_argument('-r', '--restore', action="store_true", help="restore the databases from the backups")
    p.add_argument('-b', '--backup', action="store_true", help="creates new backups from the databases")
    p.add_argument('-a', '--all', action="store_true", help="executes all tasks (this does not include the "
                                                            "compilation step, use -ac if you want to do everything)")


def configure_config(sub):
    def add_common_config_args(config_parser):
        config_parser.add_argument('url', type=str, help="a configuration api url")
        config_parser.add_argument('-l', '--login', type=str, help="a valid login")
        config_parser.add_argument('-p', '--password', type=str, help="your password")

    def configure_export(export_sub):
        p = export_sub.add_parser('export')
        p.add_argument('-o', '--output-file', type=str, help="the file where the export will be saved")
        add_common_config_args(p)

    def configure_fixguid(fixguid_sub):
        p = fixguid_sub.add_parser('fixguid')
        add_common_config_args(p)

    p = sub.add_parser('config')
    sub = p.add_subparsers(help='config-commands', dest='config_command')

    configure_export(sub)
    configure_fixguid(sub)


def build_parser():
    main_parser = ArgumentParser(description='PLS: Powerful Lannister Script v2, manages applications.')
    main_parser.add_argument('-c', '--config',
                             help="Uses a specific config file (will be config.json by default).",
                             default="config.json")

    sub = main_parser.add_subparsers(help='commands', dest='command')
    configure_dbtask(sub)
    configure_config(sub)

    return main_parser


def process(main_args):
    api = context.build(main_args.config or "config.json")

    if main_args.command == 'dbtask':
        tenants = main_args.tenants

        if len(main_args.tenants) == 1 and main_args.tenants[0] == 'all':
            tenants = [tenant_id for tenant_id in api.config['tenants']]

        if main_args.compile:
            api.compile_migrations()

        if main_args.restore or main_args.all:
            api.restore_tenants(*tenants)

        if main_args.migrate or main_args.all:
            api.migrate_tenants(*tenants)

        if main_args.backup or main_args.all:
            api.backup_tenants(*tenants)

    elif main_args.command == 'config':
        config_api = ConfigApi(main_args.url, main_args.login, main_args.password)

        if main_args.config_command == 'export':
            config_api.get_config(main_args.output_file)

        elif main_args.config_command == 'fixguid':
            config_api.fixguid()


parser = build_parser()
args = parser.parse_args()

process(args)
