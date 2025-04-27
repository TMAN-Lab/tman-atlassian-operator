#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


import os
import shutil
import sys
import pkg_resources
import requests
import yaml
from tabulate import tabulate
from atlassian_operator.utils.appDocker import AppDocker
from atlassian_operator.utils.appServices import AppServices
from atlassian_operator.utils.appLogger import AppLogger
from atlassian_operator.cli.appCli import product_alias_full_name
# from crontab import CronTab
# from crontab import CronItem


def print_tree(start_path, indent=""):
    for idx, item in enumerate(os.listdir(start_path)):
        path = os.path.join(start_path, item)
        connector = "├── " if idx < len(os.listdir(start_path)) - 1 else "└── "
        print(indent + connector + item)
        if os.path.isdir(path):
            new_indent = indent + ("│   " if idx < len(os.listdir(start_path)) - 1 else "    ")
            print_tree(path, new_indent)
    return True


class AppApi(object):
    def __init__(self, pkg_name, cmd_name, app_args):
        self.pkg_name = pkg_name
        self.cmd_name = cmd_name
        self.app_name = self.cmd_name.replace("-", "_")
        self.app_args = app_args
        self.app_config_file = os.path.join("/", "usr", "local", "etc", "{}.conf".format(self.cmd_name))
        self.app_config_exist = os.path.exists(self.app_config_file)
        self.app_app_dir = "{}-services".format(self.cmd_name)
        self.app_exec_path = os.path.abspath(".")
        self.app_home = None
        self.app_home_config = None
        self.app_home_container = None
        self.app_services = None
        if self.app_config_exist:
            with open(self.app_config_file, "r", encoding="utf-8") as f:
                config_content = yaml.safe_load(f.read())
            self.app_home = config_content.get("{}_HOME".format(self.app_name.upper()))
            self.app_home_config = config_content.get("{}_CONFIG".format(self.app_name.upper()))
            self.app_home_container = config_content.get("{}_CONTAINER".format(self.app_name.upper()))
        self.app_home_exist = os.path.exists(self.app_home) if self.app_home else False
        self.docker = AppDocker(app_name=self.app_name, app_args=self.app_args)
        self.app_products = product_alias_full_name()

    def __check_load_app_services(self, force=False):
        if self.app_services is None and self.app_home:
            self.app_services = AppServices(
                app_name=self.app_name,
                app_home=self.app_home
            )
        elif force and self.app_home:
            self.app_services = AppServices(
                app_name=self.app_name,
                app_home=self.app_home
            )
        return True

    def show(self):
        if self.app_args.get("version"):
            self.__version()
        elif self.app_args.get("config"):
            self.__config()
        return True

    def __version(self):
        try:
            pkg_version = pkg_resources.get_distribution(self.pkg_name).version
        except pkg_resources.DistributionNotFound:
            pkg_version = "0.1"
        docker_info = self.docker.docker.version()
        docker_platform = docker_info.get("Platform")
        docker_components = docker_info.get("Components")
        docker_version = ""
        docker_build = ""
        docker_api = ""
        for docker_component in docker_components:
            if docker_component.get("Name") == "Engine":
                try:
                    docker_version = docker_component.get("Version")
                    docker_build = docker_component.get("Details").get("GitCommit")
                    docker_api = docker_component.get("Details").get("ApiVersion")
                except AttributeError:
                    print("")
        version_str_install = "{} [{}] version: {}".format(self.cmd_name, self.pkg_name, pkg_version)
        version_str_python = "Python version: {}".format(sys.version)
        version_str_docker = "{} {}, build {}, API version {}".format(
            docker_platform.get("Name"),
            docker_version,
            docker_build,
            docker_api
        )
        version_str_tag = "\u00AF" * max(
            len(version_str_install),
            len(version_str_python.split("\n")[0]),
            len(version_str_docker)
        )
        print("\n".join([
            version_str_install,
            version_str_tag,
            version_str_python,
            version_str_tag,
            version_str_docker,
            version_str_tag,
        ]))
        return True

    @staticmethod
    def __list_dir(start_path="."):
        return print_tree(start_path=start_path)

    def __check_init_history(self):
        check_result = True
        if self.app_services:
            for vol in self.app_services.service_dirs:
                if not os.path.exists(vol):
                    AppLogger.failure("{} is not existed".format(os.path.basename(vol)))
                    check_result = False
        else:
            check_result = False
        if not self.app_config_exist:
            check_result = False
        return check_result

    def __config(self):
        AppLogger.launch("Check tool configuration {}".format(self.app_config_file))
        table_headers = [
            "KEY",
            "VALUE",
        ]
        table_data = list()
        if self.app_config_exist is False:
            AppLogger.failure("Config file is not existed, hava you executed 'init'?")
            return False
        with open(self.app_config_file, "r", encoding="utf-8") as f:
            config_content = yaml.safe_load(f.read())
        for config_key, config_val in config_content.items():
            table_data.append([config_key, config_val])
        print("")
        table_data.append([])
        print(tabulate(table_data, headers=table_headers))
        return True

    @staticmethod
    def __generate_product_config(product_list, tmpl_config_file_path, app_product_config_file_path):
        with open(tmpl_config_file_path, 'r') as f:
            tmpl_content = f.read()
        content_lines = list()
        db_envs = [
            " ATL_JDBC_URL:",
            " ATL_JDBC_USER:",
            " ATL_JDBC_PASSWORD:",
            " ATL_DB_DRIVER:",
            " ATL_DB_TYPE:",
            " JDBC_DRIVER:",
            " JDBC_URL:",
            " JDBC_USER:",
            " JDBC_PASSWORD:",
        ] if "postgres" in product_list else []
        for tmpl_line in tmpl_content.split("\n"):
            if any(db_env in tmpl_line for db_env in db_envs):
                content_lines.append(tmpl_line.replace("#", ""))
            else:
                content_lines.append(tmpl_line)
        config_content = "\n\n".join([
            "enable: true",
            "\n".join(content_lines)
        ])
        with open(app_product_config_file_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        AppLogger.success("Generate product config {}".format(app_product_config_file_path))
        return True

    def __init_first_time(self):
        AppLogger.launch("Check the environment of services")
        if self.docker.cli_ps():
            AppLogger.failure("Some services is already running")
            return False
        if self.app_config_exist:
            AppLogger.failure("{} config file {} is existed".format(self.cmd_name, self.app_config_file))
            return False
        AppLogger.launch("Create and init files tree")
        AppLogger.launch("Before initialization")
        self.__list_dir()
        try:
            check_result = True
            os.makedirs(os.path.join(self.app_exec_path, self.app_app_dir), exist_ok=True)
            AppLogger.launch("Generate {} config file {}".format(self.cmd_name, self.app_config_file))
            self.app_home = os.path.join(self.app_exec_path, self.app_app_dir)
            app_home_config = os.path.join(self.app_exec_path, self.app_app_dir, "config")
            app_home_container = os.path.join(self.app_exec_path, self.app_app_dir, "container")
            config_content = "\n".join([
                "# ",
                "# Default {} file".format(self.app_config_file),
                "# ",
                "{}_HOME: {}".format(self.app_name.upper(), self.app_home),
                "{}_CONFIG: {}".format(self.app_name.upper(), app_home_config),
                "{}_CONTAINER: {}".format(self.app_name.upper(), app_home_container),
            ])
            with open(self.app_config_file, "w", encoding="utf-8") as f:
                f.write(config_content)
            AppLogger.launch("Init {} services configs".format(self.cmd_name))
            tmpl_dir = pkg_resources.resource_filename(
                self.pkg_name,
                "tmpl"
            )

            for product_name in self.app_args.get("product"):
                product_config_file = "{}.yaml".format(self.app_products.get(product_name))
                os.makedirs(app_home_config, exist_ok=True)
                self.__generate_product_config(
                    product_list=self.app_args.get("product"),
                    tmpl_config_file_path=os.path.join(tmpl_dir, "config", product_config_file),
                    app_product_config_file_path=os.path.join(app_home_config, product_config_file)
                )
            AppLogger.launch("Init {} services data dir".format(self.cmd_name))
            self.__check_load_app_services()
            for vol in self.app_services.service_dirs:
                if os.path.exists(vol):
                    AppLogger.failure("{} is existed".format(os.path.basename(vol)))
                    check_result = False
            if not check_result:
                return False
            for vol in self.app_services.service_dirs:
                AppLogger.launch("Create dir {}".format(vol))
                os.makedirs(vol)
            if "nginx" in self.app_args.get("product"):
                os.makedirs(os.path.join(app_home_container, "nginx"), exist_ok=True)
                for product_name in self.app_args.get("product"):
                    product_nginx_conf_file_name = "{}.conf".format(self.app_products.get(product_name))
                    product_nginx_conf_tmpl_file = os.path.join(
                        tmpl_dir, "nginx", "conf.d", product_nginx_conf_file_name
                    )
                    if os.path.exists(product_nginx_conf_tmpl_file):
                        shutil.copy(
                            os.path.join(product_nginx_conf_tmpl_file),
                            os.path.join(app_home_container, "nginx", "conf.d", product_nginx_conf_file_name)
                        )
            if "postgres" in self.app_args.get("product"):
                os.makedirs(os.path.join(app_home_container, "postgres"), exist_ok=True)
                product_postgres_init_tmpl_path = os.path.join(
                    tmpl_dir, "postgres", "docker-entrypoint-initdb.d", "init.sql"
                )
                if os.path.exists(product_postgres_init_tmpl_path):
                    shutil.copy(
                        os.path.join(product_postgres_init_tmpl_path),
                        os.path.join(app_home_container, "postgres", "docker-entrypoint-initdb.d", "init.sql")
                    )
            AppLogger.success("Complete initialization")
            self.__list_dir()
            return True
        except Exception as e:
            AppLogger.failure(e)
            return False

    def __init_add(self):
        AppLogger.launch("Check the environment of services")
        self.__check_load_app_services()
        if not self.__check_init_history():
            self.docker.cli_ps()
            self.__list_dir()
            AppLogger.failure("Looks like no init history in this host, hava you executed 'init'?")
            return False
        if self.docker.cli_ps():
            AppLogger.warning("Some services is already running")
        # if not self.app_config_exist:
        #     AppLogger.failure("{} config file {} is existed".format(self.cmd_name, self.app_config_file))
        #     return False
        # AppLogger.launch("Create and init files tree")
        # AppLogger.launch("Before initialization")
        # self.__list_dir()
        try:
            AppLogger.launch("Init {} services configs".format(self.cmd_name))
            tmpl_dir = pkg_resources.resource_filename(
                self.pkg_name,
                "tmpl"
            )
            for product_name in self.app_args.get("product"):
                product_config_file = "{}.yaml".format(self.app_products.get(product_name))
                config_file_path = os.path.join(self.app_home_config, product_config_file)
                if os.path.exists(config_file_path):
                    AppLogger.warning("Ignore {} because {} is existed.".format(product_name, product_config_file))
                    continue
                # os.makedirs(self.app_home_config, exist_ok=True)
                self.__generate_product_config(
                    product_list=self.app_args.get("product"),
                    tmpl_config_file_path=os.path.join(tmpl_dir, "config", product_config_file),
                    app_product_config_file_path=config_file_path
                )
            AppLogger.launch("Init {} services data dir".format(self.cmd_name))
            self.__check_load_app_services(force=True)
            for vol in self.app_services.service_dirs:
                if os.path.exists(vol):
                    AppLogger.warning("{} is existed".format(os.path.basename(vol)))
                else:
                    AppLogger.launch("Create dir {}".format(vol))
                    os.makedirs(vol)
            if "nginx" in self.app_args.get("product"):
                os.makedirs(os.path.join(self.app_home_container, "nginx"), exist_ok=True)
                for product_name in self.app_args.get("product"):
                    product_nginx_conf_file_name = "{}.conf".format(self.app_products.get(product_name))
                    product_nginx_conf_tmpl_file_path = os.path.join(
                        tmpl_dir, "nginx", "conf.d", product_nginx_conf_file_name
                    )
                    product_nginx_conf_app_file_path = os.path.join(
                        self.app_home_container, "nginx", "conf.d", product_nginx_conf_file_name
                    )
                    if os.path.exists(
                        product_nginx_conf_tmpl_file_path
                    ) and not os.path.exists(
                        product_nginx_conf_app_file_path
                    ):
                        shutil.copy(
                            os.path.join(product_nginx_conf_tmpl_file_path),
                            os.path.join(product_nginx_conf_app_file_path)
                        )
            AppLogger.success("Complete initialization")
            self.__list_dir()
            return True
        except Exception as e:
            AppLogger.failure(e)
            return False

    def init(self):
        if self.app_args.get("add"):
            return self.__init_add()
        else:
            return self.__init_first_time()

    def list(self):
        AppLogger.launch("List all services")
        self.docker.cli_ps()
        return True

    def pull(self):
        AppLogger.launch("Try to pull all images")
        self.__check_load_app_services()
        for item in self.app_services.items if self.app_services else []:
            self.docker.cli_pull(service_object=item)
        return True

    def up(self):
        # self.docker.cli_ps()
        AppLogger.launch("Try to start all services")
        self.__check_load_app_services()
        if not self.__check_init_history():
            self.docker.cli_ps()
            self.__list_dir()
            AppLogger.failure("Looks like no init history in this host, hava you executed 'init'?")
            return False
        for item in self.app_services.items:
            self.docker.cli_up(service_object=item)
        self.docker.cli_ps()
        AppLogger.success("All services started")
        return True

    # def upgrade(self):
    #     upgrade_url = "{}/upgrade/callback".format(self.app_api_base_url)
    #     session = requests.session()
    #     session.get(url=upgrade_url, params={"upgrade": "started"})
    #     self.docker.cli_ps()
    #     AppLogger.launch("Try to upgrade services")
    #     if not self.__check_init_history():
    #         self.__list_dir()
    #         AppLogger.failure("Looks like no init history in this host, hava you executed 'init'?")
    #         session.get(url=upgrade_url, params={"upgrade": "skipped"})
    #         return False
    #     session.get(url=upgrade_url, params={"upgrade": "in-progress"})
    #     for item in self.app_services.items:
    #         AppLogger.launch("Check and upgrade service {}".format(item.service_name))
    #         self.docker.cli_upgrade(service_object=item)
    #     self.docker.cli_ps()
    #     session.get(url=upgrade_url, params={"upgrade": "completed"})
    #     AppLogger.success("All services are latest")
    #     session.close()
    #     return True

    def down(self):
        AppLogger.launch("Try to down all services")
        self.__check_load_app_services()
        # self.docker.cli_ps()
        if not self.__check_init_history():
            self.__list_dir()
            AppLogger.failure("Looks like no init history in this host, hava you executed 'init'?")
            return False
        for item in self.app_services.items:
            print("\tservice {}".format(item.service_name))
            self.docker.cli_down(service_object=item)
        print("")
        self.docker.cli_ps()
        AppLogger.success("All services down")
        return True

    def cleanup(self):
        AppLogger.launch("Start to cleanup all data of {} ".format(self.cmd_name))
        if self.app_home and os.path.exists(self.app_home):
            shutil.rmtree(os.path.join(self.app_home, "config"))
            AppLogger.success("Removed all configs of {}".format(self.app_name))
        if self.app_config_exist:
            os.remove(self.app_config_file)
            AppLogger.success("Removed {} config file".format(self.cmd_name))
        if self.app_home and self.app_args.get("data"):
            AppLogger.launch("Cleanup all custom data of {} services".format(self.app_name))
            shutil.rmtree(os.path.join(self.app_home, "container"))
            AppLogger.success("Removed all custom data")
        AppLogger.success("Complete cleanup")
        return True


if __name__ == "__main__":
    print("🚀 This is a cli package")
