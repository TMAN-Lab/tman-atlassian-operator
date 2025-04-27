#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


# import os
import docker
from docker.errors import NotFound
from docker.errors import ImageNotFound
from docker.errors import APIError
from docker.errors import DockerException
from tabulate import tabulate
from atlassian_operator.utils.appLogger import AppLogger


class AppDocker(object):
    def __init__(self, app_name, app_args):
        try:
            self.docker = docker.from_env()
        except DockerException as DockerError:
            AppLogger.failure("{}\nIs the docker daemon running?".format(DockerError))
            AppLogger.exit()
        self.app_name = app_name
        try:
            self.docker.networks.get(self.app_name)
        except NotFound:
            self.docker.networks.create(self.app_name, driver="bridge")
        self.app_args = app_args

    def cli_ps(self):
        table_data = list()
        table_headers = [
            "NAME",
            "CONTAINER ID",
            "PORTS",
            "CREATED",
            "STATUS",
            "IMAGE",
            "IMAGE ID",
        ]
        items = self.docker.containers.list(
            all=True,
            filters={"label": "app={}".format(self.app_name)}
        )
        for item in items:
            item_attrs = item.attrs
            item_image = item.image.attrs.get("RepoTags")
            item_status = item_attrs.get("State").get("Status")
            item_img_id = str(item_attrs.get("Image")).split(":")[-1][:12]
            item_ports = list()
            try:
                for expose_port_str, host_port_item in item_attrs.get("HostConfig", {}).get("PortBindings", {}).items():
                    item_ports.append(
                        "{}->{}".format(
                            host_port_item[0].get("HostPort"),
                            expose_port_str.split("/")[0]
                        )
                    )
            except AttributeError:
                item_ports.append("")
            try:
                item_health = "({})".format(item_attrs.get("State").get("Health").get("Status"))
            except AttributeError:
                item_health = ""
            table_data.append([
                item_attrs.get("Name").lstrip("/"),
                item.id[:12],
                ", ".join(item_ports),
                AppLogger.print_relative_time(item_attrs.get("Created")),
                "{} {}".format(item_status, item_health),
                item_image[0] if len(item_image) > 0 else "",
                item_img_id
            ])
        print("")
        app_containers = True if table_data else False
        table_data.append([])
        print(tabulate(table_data, headers=table_headers))
        return app_containers

    def __check_container(self, container_name):
        try:
            self.docker.containers.get(container_name)
            # item = self.docker.containers.get(container_name)
            # assert item.attrs.get("State").get("Status") == "running"
            return True
        except NotFound:
            return False
        # except AssertionError:
        #     return False

    def cli_up(self, service_object, upgrade=False):
        try:
            assert not self.__check_container(service_object.container_name)
            if not upgrade:
                service_object.labels["app"] = self.app_name
            self.docker.containers.run(
                image=service_object.image,
                name=service_object.container_name,
                detach=True,
                ports=service_object.ports,
                environment=service_object.environment,
                volumes=service_object.volumes,
                restart_policy={"Name": service_object.restart},
                mem_limit=service_object.memory,
                nano_cpus=service_object.cpus,
                labels=service_object.labels,
                links=service_object.links,
                network=self.app_name,
                command=service_object.command
            )
        except APIError or DockerException as dockerError:
            AppLogger.tab_failure(dockerError)
        except AssertionError:
            AppLogger.tab_warning("{} is already running".format(service_object.container_name))
        return True

    def cli_down(self, service_object):
        if not self.__check_container(service_object.container_name):
            return True
        try:
            container = self.docker.containers.get(service_object.container_name)
            container.stop()
            container.remove()
        except APIError or DockerException as dockerError:
            AppLogger.tab_failure(dockerError)
        return True

    def __get_image_digest(self, image_tag):
        try:
            image = self.docker.images.get(image_tag)
        except ImageNotFound:
            return None
        if 'RepoDigests' in image.attrs and image.attrs['RepoDigests']:
            img_digest = image.attrs['RepoDigests'][0]
            AppLogger.tab_success(img_digest)
        else:
            img_digest = None
            AppLogger.tab_warning(img_digest)
        return img_digest

    def __get_container_mirror_label(self, container_name):
        try:
            container = self.docker.containers.get(container_name)
        except NotFound:
            return None
        if container.labels.get("mirror") == "true":
            return True
        else:
            return False

    def cli_pull(self, service_object):
        pulled_new = True
        try:
            AppLogger.tab_launch("Check current {}".format(service_object.image))
            pull_a = self.__get_image_digest(service_object.image)
            AppLogger.tab_launch("Check image from Docker Hub")
            self.docker.images.pull(service_object.image)
            pull_b = self.__get_image_digest(service_object.image)
            if pull_a == pull_b:
                pulled_new = False
        except NotFound:
            pulled_new = True
        return pulled_new

    def cli_upgrade(self, service_object):
        try:
            item = self.docker.containers.get(service_object.container_name)
            if self.cli_pull(service_object):
                AppLogger.tab_warning("Found new latest image")
                for env_item in item.attrs["Config"]["Env"]:
                    env_k, env_v = env_item.split("=")
                    if env_k.startswith("{}_".format(self.app_name.upper())):
                        service_object.environment[env_k] = env_v
                service_object.labels["app"] = item.attrs["Config"]["Labels"].get("app")
                service_object.labels["mirror"] = item.attrs["Config"]["Labels"].get("mirror")
                AppLogger.tab_warning("Labels: {}".format(service_object.labels))
                self.cli_down(service_object)
                self.cli_up(service_object, upgrade=True)
                AppLogger.tab_success("Upgraded this service")
            else:
                AppLogger.tab_success("No new latest image, skip to upgrade this service")
            return True
        except NotFound:
            AppLogger.tab_failure("Not Found container")
            return False


if __name__ == "__main__":
    print("🚀 This is a docker client package")
