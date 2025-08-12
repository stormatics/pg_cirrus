# pg_cirrus — Hassle-Free PostgreSQL Cluster Setup

**pg_cirrus** is a utility designed to simplify the deployment of a **highly available 3-node PostgreSQL cluster** on Linux-based systems.

## Overview

The primary objective of this project is to enable users to configure a robust, fault-tolerant PostgreSQL cluster with minimal manual intervention.  
The configuration follows best practices for **high availability (HA)** while keeping the process simple and repeatable.

The name **cirrus** is inspired by the **cirrus cloud** — thin, wispy clouds that form at high altitudes — reflecting the lightweight yet reliable nature of the tool.

## Features
- Automated deployment of a **3-node HA PostgreSQL cluster**.
- Uses **streaming replication**.
- Built with **Python** and **Ansible** for flexibility and automation.
- Designed for minimal configuration overhead.

## Supported Platforms

This tool has been **tested and verified** on:
- **Ubuntu**
- **Red Hat Enterprise Linux (RHEL)**

It may also work on other Linux distributions with compatible PostgreSQL and Ansible versions, but they are not officially tested.

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
You can find a full copy of the license in the [LICENSE](LICENSE) file.
