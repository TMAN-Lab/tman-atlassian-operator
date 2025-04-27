#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: will.shi@tman.ltd


from setuptools import find_packages, setup
import os

URL = 'https://en.tman.ltd'

NAME = 'atlassian-operator'

if os.getenv("BITBUCKET_TAG"):
    VERSION = os.getenv("BITBUCKET_TAG")
else:
    with open("version_dev.txt", 'r') as f:
        version = f.read().strip()
    ver_major, ver_minor = version.split(".")
    ver_next = int(ver_minor) + 1
    VERSION = ".".join([str(ver_major), str(ver_next)])
    with open("version_dev.txt", 'w') as f:
        f.write(VERSION)

DESCRIPTION = 'Deploying Atlassian Products with Docker'

if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = DESCRIPTION

AUTHOR = 'Will'
AUTHOR_EMAIL = 'will.shi@tman.ltd'

LICENSE = 'Apache'

PLATFORMS = [
    'linux',
]

REQUIRES = [
    'PyYAML',
    'docker',
    'tabulate',
    'requests',
]

CONSOLE_SCRIPTS = 'atlas-operator=atlassian_operator.main:main'

PKG_DATA = {
    "atlassian_operator": [
        "tmpl/config/*yaml",
        "tmpl/nginx/conf.d/*conf",
        "tmpl/postgres/docker-entrypoint-initdb.d/*sql",
    ]
}

setup(
    name=NAME,
    version=VERSION,
    description=(
        DESCRIPTION
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    package_data=PKG_DATA,
    platforms=PLATFORMS,
    url=URL,
    install_requires=REQUIRES,
    entry_points={
        'console_scripts': [CONSOLE_SCRIPTS],
    }
)
