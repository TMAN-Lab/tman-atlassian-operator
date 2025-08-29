#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


import os
import yaml


class AppSvcObject(object):
    def __init__(self, service_name, image_tag, cpus, memory):
        self.__one_cpu = 1000000000
        self.service_name = service_name
        self.container_name = service_name
        self.image = image_tag
        self.restart = "always"
        self.cpus = int(float(cpus) * self.__one_cpu)
        self.memory = memory
        self.volumes = dict()
        self.environment = dict()
        self.ports = dict()
        self.links = dict()
        self.labels = dict()
        self.command = None

    def bind_volume(self, host_path, container_path):
        self.volumes[host_path] = {
             "bind": container_path,
             "mode": "rw"
        }
        return True


class AppServices(object):
    def __init__(self, app_name, app_home):
        self.items = list()
        self.links = dict()
        self.service_dirs = list()
        self.app_path_config = os.path.join(app_home, "config")
        self.app_path_container = os.path.join(app_home, "container")

        up_db = list()
        up_product = list()
        up_lb = list()
        for service_config_file in os.listdir(self.app_path_config):
            if service_config_file == "nginx.yaml":
                up_lb.append(service_config_file)
            elif service_config_file in ["postgres.yaml"]:
                up_db.append(service_config_file)
            else:
                up_product.append(service_config_file)
        up_sorted_list = up_db + up_product + up_lb
        for service_config_file in up_sorted_list:
            with open(os.path.join(self.app_path_config, service_config_file), 'r', encoding='utf-8') as f:
                config_content = yaml.safe_load(f.read())
            if str(config_content.get("enable")).lower() not in ["yes", "true"]:
                continue
            item = AppSvcObject(
                service_name="{}-{}".format(app_name.replace("_", "-").lower(), config_content.get("service")),
                image_tag=config_content.get("image"),
                cpus=config_content.get("cpus"),
                memory=config_content.get("memory")
            )

            service_ports = config_content.get("port") if config_content.get("port") else []
            for service_port in service_ports:
                item.ports["{}/tcp".format(service_port)] = service_port

            service_envs = config_content.get("environment") if config_content.get("environment") else {}
            for env_key, env_val in service_envs.items():
                item.environment[env_key] = env_val

            service_vols = config_content.get("volume") if config_content.get("volume") else []
            for service_vol in service_vols:
                item.bind_volume(
                    str(service_vol).split(":")[0],
                    str(service_vol).split(":")[1]
                )

            if config_content.get("service") in ["jira-software", "jira-servicemanagement"]:
                item.bind_volume(
                    "{}/jira".format(self.app_path_container),
                    "/var/atlassian/application-data/jira"
                )
            elif config_content.get("service") in ["confluence", "bitbucket", "bamboo", "bamboo-agent", "crowd"]:
                item.bind_volume(
                    "{}/{}".format(self.app_path_container, config_content.get("service")),
                    "/var/atlassian/application-data/{}".format(config_content.get("service"))
                )
            elif config_content.get("service") in ["postgres"]:
                item.bind_volume(
                    "{}/postgres/data".format(self.app_path_container),
                    "/var/lib/postgresql/data"
                )
                item.bind_volume(
                    "{}/postgres/docker-entrypoint-initdb.d".format(self.app_path_container),
                    "/docker-entrypoint-initdb.d"
                )
            elif config_content.get("service") in ["nginx"]:
                item.bind_volume(
                    "{}/nginx/conf.d".format(self.app_path_container),
                    "/etc/nginx/conf.d"
                )
                item.bind_volume(
                    "{}/nginx/ssl".format(self.app_path_container),
                    "/etc/nginx/ssl"
                )
                item.bind_volume(
                    "{}/nginx/html".format(self.app_path_container),
                    "/etc/nginx/html"
                )

            self.items.append(item)
            self.links[item.service_name] = item.service_name
            for host_dir in item.volumes.keys():
                self.service_dirs.append(host_dir)

        for item in self.items:
            item.links = self.links


if __name__ == "__main__":
    print("🚀 This is a docker container services package")
