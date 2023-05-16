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
Create postgres user and give it sudo privileges

```
$ sudo adduser postgres
$ sudo usermod -aG sudo postgres
```

### Configure Pgpool Node

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
Generate ssh key-pair for root user if key-pair is not already generated

**NOTE**: If you have already generated public key of root user you may skip this step

```
$ sudo su -
$ ssh-keygen 
```
Copy public key of root user on pgpool host to standby1, standby2 and primary hosts for ssh passwordless access

```
$ sudo su -
$ ssh-copy-id postgres@$PRIMARY_IP
$ ssh-copy-id postgres@$STANDBY1_IP
$ ssh-copy-id postgres@$STANDBY2_IP
```
Clone github repository

```
$ git clone https://github.com/stormatics/pg_cirrus
```
Go into the directory 

```
$ cd pg_cirrus/3-node-cluster/
```
 
### Prepare hosts.yml.in file

```
$ mv hosts.yml.in hosts.yml
```

**NOTE**: Replace the fields ansible_host and ansible_become with your ip addresses and passwords. You can find your ip address on primary, standby1 and standby2 hosts using ifconfig command.

### Run ansible playbook

```
$ sudo ansible-playbook -i hosts.yml setup.yml
```
Your 3-node cluster with failover must now be running smoothly 
