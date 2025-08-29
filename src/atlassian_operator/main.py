#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


import sys
from atlassian_operator.cli.appCli import AppParser
from atlassian_operator.cli.appApi import AppApi
from atlassian_operator.utils.appLogger import AppLogger


def main():
    pkg_name = "atlassian_operator"
    cmd_name = "atlas-operator"
    app_name = cmd_name.replace("-", "_")
    app_cli_parser = AppParser(app_name=app_name)
    parser = app_cli_parser.parser

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args_cmd = args.command

    if args_cmd == "show":
        if not args.__dict__.get("version") and not args.__dict__.get("config"):
            app_cli_parser.sub_parser_show.error(sys.stderr)
        elif args.__dict__.get("version") and args.__dict__.get("config"):
            app_cli_parser.sub_parser_show.error(sys.stderr)

    AppLogger.logo()
    app_cli = AppApi(pkg_name=pkg_name, cmd_name=cmd_name, app_args=args.__dict__)
    try:
        app_cmd = getattr(app_cli, args_cmd)
        app_cmd()
        return True
    except AttributeError as e:
        AppLogger.failure(e)
        AppLogger.failure("Oops, some failures during execute command [{}]".format(args_cmd))
        return False


if __name__ == "__main__":
    print("🚀 This is Atlassian Operator main script")
