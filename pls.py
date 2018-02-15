import os
import sqlite3
from argparse import ArgumentParser

def setup_db(remove=False):
    if remove and os.path.exists('./config.db'):
        os.remove('./config.db')

    conn = sqlite3.connect('config.db')
    c = conn.cursor()
    try:
        c.executescript("""
            create table if not exists servers
            (
                name varchar(50) primary key,
                hostname varchar(50),
                login varchar(50),
                password varchar(50),
                install_path varchar(50)
            );
            create table if not exists tenants
            (
                name varchar(50) primary key,
                app_name varchar(50),
                server_id varchar(50),
                config_db_name varchar(50),
                public_db_name varchar(50)
            );
        """)
        conn.commit()
    finally:
        conn.close()

def seed_db():
    Server.create('localhost', 'localhost', 'sa', 'P@assw0rd', r'C:\Program Files\Microsoft SQL Server\MSSQL14.MSSQLSERVER\MSSQL')

def with_cursor(func):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    return func(cursor)

class Server:
    def __init__(self, *args):
        (self.name, self.hostname, self.login, self.password, self.install_path) = args

    def __str__(self):
        return f'<Server:({self.name},{self.hostname})>'

    @staticmethod
    def all():
        def __inner(cursor):
            cursor.execute('SELECT * FROM servers')
            return [Server(*row) for row in cursor.fetchall()]
        return with_cursor(__inner)

    @staticmethod
    def one(name):
        def __inner(cursor):
            cursor.execute('SELECT * FROM servers WHERE name=?', (name,))
            return Server(*cursor.fetchone())
        return with_cursor(__inner)

    @staticmethod
    def create(name, hostname, login, password, install_path):
        def __inner(cursor):        
            cursor.execute('REPLACE INTO servers VALUES (?, ?, ?, ?, ?)', (name, hostname, login, password, install_path))
        return with_cursor(__inner)

class Tenant:
    def __init__(self, *args):
        (self.name, self.app_name, self.server_id, self.config_db_name, self.public_db_name) = args

    def __str__(self):
        return f'<Tenant:({self.name},{self.server_id},{self.config_db_name},{self.public_db_name})>'

    @staticmethod
    def all():
        def __inner(cursor):
            cursor.execute('SELECT * FROM tenants')
            return [Tenant(*row) for row in cursor.fetchall()]
        return with_cursor(__inner)

    @staticmethod
    def one(name):
        def __inner(cursor):
            cursor.execute('SELECT * FROM tenants WHERE name=?', (name,))
            return Server(*cursor.fetchone())
        return with_cursor(__inner)

    @staticmethod
    def create(name, app_name, server_id, config_db_name, public_db_name):
        def __inner(cursor):        
            cursor.execute('REPLACE INTO tenants VALUES (?, ?, ?, ?, ?)', (name, app_name, server_id, config_db_name, public_db_name))
        return with_cursor(__inner)        

def setup_server_parser(target):
    parser = target.add_parser(name="server", description="connect to a database server")
    subparser = parser.add_subparsers(dest='server_command')
    
    parser = subparser.add_parser(name='add', description='Stores information relative to a new database server, this can be reuse later with its name.')
    parser.add_argument('name', help='the server name, this must be unique and can be used to reference a server in other commands')
    parser.add_argument('-l', '--login', required=True)
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('-H', '--hostname', required=True, help='the the server URI')
    parser.add_argument('-i', '--install_path', required=True, help='the server install path')
    
    subparser.add_parser(name='list', description='Lists all available connected servers.')

def setup_tenant_parser(target):
    parser = target.add_parser(name='tenant', description='add a new tenant')
    subparser = parser.add_subparsers(dest='tenant_command')
    
    add_parser = subparser.add_parser(name='add', description='Stores the informations relative to a new tenant (config_db, etc.)')
    add_parser.add_argument('name', help='the tenant name, this must be unique and can be used to reference a tenant in other commands')
    add_parser.add_argument('--config', required=True, help='the config db name')
    add_parser.add_argument('--public', required=True, help='the public db name')
    add_parser.add_argument('--server', required=True, help='the database server which contains the databases')
    add_parser.add_argument('--appname', help='the application name (will override any backup restoration)')

    subparser.add_parser(name='list', description='Lists all available connected tenants.')

def setup_backup_parser(target):
    parser = target.add_parser(name="backup", description="backup applications into .bak files at a specified location")
    parser.add_argument('-f', '--backup-file', help="the backup file location")

def setup_restore_parser(target):
    parser = target.add_parser(name="restore", description="restore an application from the provided .bak files at a specified location")
    parser.add_argument('-f', '--backup-file', help="the backup file location")    

def process_add_server(args):
    Server.create(args.name, args.hostname, args.login, args.password, args.install_path)

def process_add_tenant(args):
    Tenant.create(args.name, args.appname, args.server, args.config, args.public)

def process_list_servers(args):
    [print(s.name) for s in Server.all()]

def process_list_tenants(args):
    [print(s.name) for s in Tenant.all()]

def process(args):
    if args.command == 'server':
        if args.server_command == 'add':
            process_add_server(args)
        elif args.server_command == 'list':
            process_list_servers(args)
    elif args.command == 'tenant':
        if args.tenant_command == 'add':
            process_add_tenant(args)
        elif args.tenant_command == 'list':
            process_list_tenants(args)
        
def create_parser():
    parser = ArgumentParser(
        description='PLS.py Powerful Lannister Script (v2)',
        prog='pls')

    sub_parsers = parser.add_subparsers(dest='command')

    setup_backup_parser(sub_parsers)
    setup_restore_parser(sub_parsers)
    setup_server_parser(sub_parsers)
    setup_tenant_parser(sub_parsers)
    
    return parser

def run(args=None):
    setup_db(True)
    seed_db()
    parser = create_parser()
    process(parser.parse_args(args))

run()
