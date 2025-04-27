#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


import sys
import argparse


class OptObj(object):
    def __init__(self, str_kv):
        self.name = str_kv.get("name")
        self.action = str_kv.get("action")
        self.help = str_kv.get("help")
        self.type = str_kv.get("type")
        self.choices = str_kv.get("choices")


def product_alias_full_name():
    return {
        "nginx": "nginx",
        "postgres": "postgres",
        "jira": "jira-software",
        "jsm": "jira-service-management",
        "conf": "confluence",
        "bitbucket": "bitbucket",
        "bamboo": "bamboo",
        "bamboo-agent": "bamboo-agent",
    }


class OptItems(object):
    def __init__(self):
        self.add = OptObj({
            "name": "--add",
            "action": "store_true",
            "help": "Optional. Use --add to add product/s after first time init"
        })
        self.product = OptObj({
            "name": "--product",
            "action": "append",
            "help": "e.g. --product jira --product conf",
            "type": str,
            "choices": product_alias_full_name().keys()
        })


class AppArgumentParser(argparse.ArgumentParser):
    def error(self, message: str):
        self.print_help(sys.stderr)
        sys.exit(1)


class AppParser(object):
    def __init__(self, app_name):
        self.app_name = app_name.upper().replace("_", " ")
        self.parser = AppArgumentParser(description="")

        sub_parsers = self.parser.add_subparsers(
            dest="command",
            help=""
        )

        arg_items = OptItems()

        sub_parser_show = sub_parsers.add_parser(
            "show",
            help="Show some basic information"
        )
        sub_parser_show.add_argument(
            "--version",
            action="store_true",
            help="Show all versions of tools"
        )
        sub_parser_show.add_argument(
            "--config",
            action="store_true",
            help="Show base configuration path"
        )
        self.sub_parser_show = sub_parser_show

        sub_parser_init = sub_parsers.add_parser(
            "init",
            help="Init the workspace and config of {}. ".format(self.app_name)
        )
        sub_parser_init.add_argument(
            arg_items.product.name,
            action=arg_items.product.action,
            help=arg_items.product.help,
            type=arg_items.product.type,
            choices=arg_items.product.choices,
            required=True
        )
        sub_parser_init.add_argument(
            arg_items.add.name,
            action=arg_items.add.action,
            help=arg_items.add.help
        )

        sub_parser_cleanup = sub_parsers.add_parser(
            "cleanup",
            help="Remove {} config, if you want to remove all files under {} workspace, please add --data".format(
                self.app_name, self.app_name
            )
        )
        sub_parser_cleanup.add_argument(
            "--data",
            action="store_true",
            help="Remove all files under {} workspace".format(self.app_name)
        )

        sub_parsers.add_parser(
            "pull",
            help="Pull all images of {}.".format(self.app_name)
        )

        sub_parsers.add_parser(
            "up",
            help="Up all containers of {} services.".format(self.app_name)
        )

        # sub_parsers.add_parser("upgrade", help="Upgrade the services which has new image")

        sub_parsers.add_parser(
            "down",
            help="Stop all services and down all containers"
        )

        sub_parsers.add_parser(
            "list",
            help="List all service containers"
        )


if __name__ == "__main__":
    print("🚀 This is Atlassian Operator CLI script")
