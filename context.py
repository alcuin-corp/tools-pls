from target import Target
from tenant import Tenant, set_appname
from migrator import Migrator
from server import Server
import logger
import subprocess as sp
import os
import json
import copy
import sys


def must_exist(message):
    def wrapper(func):
        def decorator(filename):
            if not (os.path.exists(filename)):
                print(f"{filename} not found, {message}")
                sys.exit()
            return func(filename)

        return decorator

    return wrapper


def with_default(default_data):
    def wrapper(func):
        def decorator(filename):
            if not (os.path.exists(filename)):
                f = open(filename, 'w')
                f.write(json.dumps(default_data, sort_keys=True, indent=4))
                f.close()
            return func(filename)
        return decorator
    return wrapper


def load_file(filename):
    f = open(filename, 'r')
    config = json.load(f)
    f.close()
    return config


def save_file(content, filename):
    f = open(filename, 'w')
    f.write(json.dumps(content, default=lambda o: o.__dict__, sort_keys=True, indent=4))
    f.flush()


@with_default({
    "alcuin_root_path": "",
    "msbuild_exe": "",
    "backup_directory": "",
    "config_migration_dll": "",
    "public_migration_dll": "",
    "migrator_exe": "",
})
def load_settings(filename):
    return load_file(filename)


@must_exist(
    "this might be because you do not have a configuration file, see the file config.example.json for a template.")
def load_config(filename):
    return load_file(filename)


def build(config_filename: str = 'config.json', settings_filename: str = 'settings.json'):
    return Context(
        settings=load_settings(settings_filename),
        config=load_config(config_filename),
    )


class Context(logger.Logger):
    def __init__(self, settings, config):
        self.settings = settings
        self.config = config

    def __get_migrator(self, target):
        if target.target_type == 'public':
            return Migrator(self.settings["migrator_exe"], self.settings["public_migration_dll"])
        elif target.target_type == 'config':
            return Migrator(self.settings["migrator_exe"], self.settings["config_migration_dll"])
        else:
            raise Exception("Unkown target type: " + target.target_type)

    def compile(self, csproj_file):
        msbuild = self.settings['msbuild_exe']
        sp.call(f'"{msbuild}" "{csproj_file}"')

    def compile_migrations(self):
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            self.error(
                'Compilation can only be executed under an elevated environment, please run this task as an '
                'administrator.')
            quit()

        root = self.settings['alcuin_root_directory']

        if not os.path.exists('x:/'):
            sp.call(f'"{root}"/x.bat')
            self.ok('X has been mounted')

        self.compile(f'{root}/Migration/Alcuin.Migration.Application/Alcuin.Migration.Application.csproj')
        self.compile(f'{root}/Migration/Alcuin.Migration.Configuration/Alcuin.Migration.Configuration.csproj')
        self.ok(f'Projects compiled successfully')

    def migrate_targets(self, *targets):
        for target in targets:
            server = self.get_server(target.server_id)
            self.__get_migrator(target).migrate(server.data_source, target.db_name)

    def restore_targets(self, *targets):
        for target in targets:
            server = self.get_server(target.server_id)
            server.restore(target.db_name, target.backup_filename)

    def backup_targets(self, *targets):
        for target in targets:
            server = self.get_server(target.server_id)
            server.backup(target.db_name, target.backup_filename)

    def save(self, config_filename: str = 'config.json', settings_filename: str = 'settings.json'):
        save_file(self.config, config_filename)
        save_file(self.settings, settings_filename)
        self.ok(f'New configuration has been written.')

    def get_server(self, server_id):
        data = {k: v for k, v in self.config["servers"][server_id].items()}
        data["server_id"] = server_id
        return Server(**data)

    def get_tenants(self):
        for tenant_id in self.config["tenants"]:
            yield self.get_tenant(tenant_id)

    def get_tenant(self, tenant_id):
        data = self.config["tenants"][tenant_id]
        targets = []
        for target_data in data["targets"]:
            targets.append(Target(
                db_name=target_data["db_name"],
                target_type=target_data["target_type"],
                server_id=target_data["server_id"],
                backup_filename=target_data["backup_filename"],
            ))

        return Tenant(
            tenant_id=tenant_id,            
            name=data.get("name"),
            targets=targets,
        )

    def restore_tenants(self, *tenant_id_list):
        for tenant_id in tenant_id_list:
            tenant = self.get_tenant(tenant_id)
            self.restore_targets(*tenant.targets)
            self.ok(f'Tenant {tenant_id} has been restored successfully')
            if tenant.name:
                set_appname(self.get_server, tenant)
                self.ok(f'Tenant name has been reset to {tenant.name}')

    def migrate_tenants(self, *tenant_id_list):
        for tenant_id in tenant_id_list:
            tenant = self.get_tenant(tenant_id)
            self.migrate_targets(*tenant.targets)
            self.ok(f'Tenant {tenant_id} has been migrated successfully')

    def backup_tenants(self, *tenant_id_list):
        for tenant_id in tenant_id_list:
            tenant = self.get_tenant(tenant_id)
            self.backup_targets(*tenant.targets)
            self.ok(f'Tenant {tenant_id} has been saved successfully')

    def remove_tenant(self, tenant_name):
        new_config = copy.deepcopy(self.config)
        new_settings = copy.deepcopy(self.settings)
        del new_config["tenants"][tenant_name]
        self.ok(f'Tenant {tenant_name} removed from configuration file.')
        return Context(new_settings, new_config)

    def create_tenant(self, tenant_name, **kwargs):
        server_id = kwargs.get("server_id") or 'localhost'
        tenant_id = kwargs.get('tenant_id') or tenant_name
        config_postfix = kwargs.get("config_postfix") or '_ADM'
        public_db_name = kwargs.get("public_db_name") or tenant_name
        public_filename = kwargs.get("public_filename") or tenant_name + '.bak'
        config_db_name = kwargs.get("config_db_name") or tenant_name + config_postfix
        config_filename = kwargs.get("config_filename") or tenant_name + config_postfix + '.bak'
        public_target = {
            'db_name': public_db_name,
            'backup_filename': public_filename,
            'server_id': server_id,
            'target_type': "public"
        }
        config_target = {
            'db_name': config_db_name,
            'backup_filename': config_filename,
            'server_id': server_id,
            'target_type': "config"
        }
        tenant = {
            'tenant_id': tenant_id,
            'name': tenant_name,
            'targets': [public_target, config_target],
        }
        new_config = copy.deepcopy(self.config)
        new_settings = copy.deepcopy(self.settings)
        new_config["tenants"].update({tenant_id: tenant})
        self.ok(f'Tenant {tenant_name} added to configuration file.')
        return Context(new_settings, new_config)
