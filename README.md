# Atlassian Operator

*Powered by [TMAN Consulting](https://en.tman.ltd)*

```text
   ___ ________   ___   _______________   _  __  ____                    __          
  / _ /_  __/ /  / _ | / __/ __/  _/ _ | / |/ / / __ \___  ___ _______ _/ /____  ____
 / __ |/ / / /__/ __ |_\ \_\ \_/ // __ |/    / / /_/ / _ \/ -_) __/ _ `/ __/ _ \/ __/
/_/ |_/_/ /____/_/ |_/___/___/___/_/ |_/_/|_/  \____/ .__/\__/_/  \_,_/\__/\___/_/   
                                                   /_/                               
```

> A Python-powered tool to simplify deployment and management of Atlassian products (Jira, Confluence, Bitbucket, Bamboo) using Docker containers.

----

## 🚀 Key Features

- Automated Provisioning: One-click deploy Jira, Confluence, or Bitbucket with pre-configured settings.
- Docker Orchestration: Abstracts complex Docker commands into simple Python operations.
- Persistent Storage: Auto-configure volumes for data persistence across restarts.
- Cluster Support: Deploy high-availability setups with load balancing.
- Configuration Management: Generate `server.xml`, `setenv.sh`, and database connectors automatically.

----

## ⚡️ Quick Start

### 1️⃣ Check preconditions

- Python >= 3
- pip
- Docker >= 20

### 2️⃣ Install `atlassian-operator` tool

```bash
pip install atlassian-operator
```

### 3️⃣ Init and modify configuration

```bash
atlas-operator init --product postgres --product jira
```

### 4️⃣ Up products containers

```bash
atlas-operator up 
```

It will be spent more time to pull images if this is the first time to run this command. 

----

## 📦 Installation

```bash
pip install atlassian-operator
atlas-operator show --version
```

----

## 🍺 Basic Usage

```text
usage: atlas-operator [-h] {show,init,cleanup,pull,up,down,list} ...

positional arguments:
  {show,init,cleanup,pull,up,down,list}
    show                Show some basic information
    init                Init the workspace and config of ATLAS OPERATOR.
    cleanup             Remove ATLAS OPERATOR config, if you want to remove all files under ATLAS OPERATOR workspace, please add --data
    pull                Pull all images of ATLAS OPERATOR.
    up                  Up all containers of ATLAS OPERATOR services.
    down                Stop all services and down all containers
    list                List all service containers

optional arguments:
  -h, --help            show this help message and exit
```

### show

```text
usage: atlas-operator show [-h] [--version] [--config]

optional arguments:
  -h, --help  show this help message and exit
  --version   Show all versions of tools
  --config    Show base configuration path
```

### init

```text
usage: atlas-operator init [-h] --product {nginx,postgres,jira,jsm,conf,bitbucket}

optional arguments:
  -h, --help            show this help message and exit
  --product {nginx,postgres,jira,jsm,conf,bitbucket,bamboo}
                        e.g. --product jira 
                        e.g. --product jira --product conf
```

### up

Need to check and modify the products configuration before run `atlas-operator up` to start services.

All configuration files can be found when you run `atlas-operator show --config` 

----

## 🌍 License

`Apache License 2.0`

----

## 📚 Resources

### Atlassian Docker Images

- [Jira Software `atlassian/jira-software:<tag>`](https://hub.docker.com/r/atlassian/jira-software)
- [Jira Service Management `atlassian/jira-servicemanagement:<tag>`](https://hub.docker.com/r/atlassian/jira-servicemanagement)
- [Confluence `atlassian/confluence:<tag>`](https://hub.docker.com/r/atlassian/confluence)

### Atlassian Official Docs

- [Jira Data Center Container](https://atlassian.github.io/data-center-helm-charts/containers/JIRA/)
- [Confluence Data Center Container](https://atlassian.github.io/data-center-helm-charts/containers/CONFLUENCE/)
- [Bitbucket Data Center Container](https://atlassian.github.io/data-center-helm-charts/containers/BITBUCKET/)
- [Bamboo Container](https://atlassian.github.io/data-center-helm-charts/containers/BAMBOO/)
- [Bamboo Agent Container](https://atlassian.github.io/data-center-helm-charts/containers/BAMBOO-AGENT/)
- [Crowd Data Center Container](https://atlassian.github.io/data-center-helm-charts/containers/CROWD/)