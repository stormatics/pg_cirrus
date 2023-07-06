# 3-node-cluster

This directory contains script files for setting up 3-node highly available PostgreSQL cluster.

## Prerequisites

### Configure Primary, Standby1 and Standby2 Nodes

Update local apt package manager

```
$ sudo apt-get update -y
```
Install OpenSSH Server

```
$ sudo apt-get install openssh-server -y
```
Create postgres user and give it passwordless sudo privileges

```
$ sudo adduser postgres
$ sudo visudo
```
Add the following string at the end of visudo file

```
postgres ALL=(ALL) NOPASSWD:ALL
```
### Configure pgpool Node

Update local apt package manager

```
$ sudo apt-get update -y
```
Install OpenSSH Server

```
$ sudo apt-get install openssh-server -y
```
Install Ansible

```
$ sudo apt-get install ansible -y
```
Install Git

```
$ sudo apt-get install git -y
```
Install python3

```
$ sudo apt-get install python3 -y
```
Generate ssh key-pair for root user if key-pair is not already generated

**NOTE**: If you have already generated public key of root user you may skip this step

```
$ sudo su -
$ ssh-keygen 
```
Copy public key of root user on pgpool host to standby1, standby2 and primary hosts for ssh passwordless access

```
$ sudo su -
$ ssh-copy-id postgres@<PRIMARY_IP>
$ ssh-copy-id postgres@<STANDBY1_IP>
$ ssh-copy-id postgres@<STANDBY2_IP>
```
Clone github repository

```
$ git clone https://github.com/stormatics/pg_cirrus
```
Go into the directory 

```
$ cd pg_cirrus/3-node-cluster/
```
 
Create vault.yml file using Ansible vault

```
$ ansible-vault create vault.yml
```
You will be prompted for vault password, after entering vault password vault file will be open.

Write following lines inside vault.yml

```
PFILE_PASSWORD: <your_postgres_database_password>
REPUSER_PASSWORD: <your_replication_user_password>
```

Create file to store vault password
```
$ touch <file_name>
$ chmod 0600 <file_name>
```
Write vault password inside this file

### Execute pg_cirrus
```
$ python3 main.py
```
