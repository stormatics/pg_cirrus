# 3-node-cluster

This directory contains script files for setting up 3-node highly available PostgreSQL cluster.

## Prerequisites

### Configure Primary, Standby1 and Standby2 Nodes


```
# Update local apt package manager
sudo apt-get update -y

# Install OpenSSH Server
sudo apt-get install openssh-server -y

# Create postgres user and give it passwordless sudo privileges
sudo adduser postgres
sudo visudo
```

Add the following string at the end of visudo file

```
postgres ALL=(ALL) NOPASSWD:ALL
```
For AWS/EC2 get your id_rsa.pub of postgres user on pg_cirrus node and run the following command on primary, standby1 and standby2 nodes
```
mkdir -p ~/.ssh && echo '<$PG_CIRRUS_NODE_ID_RSA.PUB>' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```
**NOTE**: On AWS/EC2, update the inbound rule for the primary, standby1 and standby2 node to allow All **ICMP - IPv4 traffic** from the pg_cirrus node.

### Configure pgpool Node

```
# Update local apt package manager
sudo apt-get update -y

#Install OpenSSH Server
sudo apt-get install openssh-server -y

# Install Ansible
sudo apt-get install ansible -y

# Install Git
sudo apt-get install git -y

# Install python3
sudo apt-get install python3 -y

# Create postgres user and give it passwordless sudo privileges
sudo adduser postgres
sudo visudo
```
Add the following string at the end of visudo file

```
postgres ALL=(ALL) NOPASSWD:ALL
```
Switch to postgres user
```
sudo su postgres 
```
Generate ssh key-pair if key-pair is not already generated

**NOTE**: If you have already generated public key of postgres user you may skip this step

```
ssh-keygen -t rsa
```
Copy the public key of postgres user on pgpool host to standby1, standby2 and primary hosts for ssh passwordless access (For AWS/EC2 refer to above Configure Primary, Standby1 and Standby2 Nodes section)

```
ssh-copy-id postgres@<PRIMARY_IP>
ssh-copy-id postgres@<STANDBY1_IP>
ssh-copy-id postgres@<STANDBY2_IP>
```

Clone github repository

```
git clone https://github.com/stormatics/pg_cirrus
```
Go into the directory 

```
cd pg_cirrus/3-node-cluster/
```
 
Create vault.yml file using Ansible vault

```
ansible-vault create vault.yml
```
You will be prompted for vault password, after entering vault password vault file will be open.

Write following lines inside vault.yml

```
PSQL_SERVER_PASSWORD: <your_psql_server_password>
REPUSER_PASSWORD: <your_replication_user_password>
```

Create file to store vault password
```
touch <file_name>
chmod 0600 <file_name>
```
Write vault password inside this file

### Execute pg_cirrus
```
python3 deploy.py
```
