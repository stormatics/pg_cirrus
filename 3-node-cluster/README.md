# 3-node-cluster

This directory contains script files for setting up a 3-node highly available PostgreSQL cluster.

## Prerequisites

### Configure Primary, Standby1 and Standby2 Nodes
```
# Update local apt package manager
sudo apt-get update -y

# Install OpenSSH Server
sudo apt-get install openssh-server -y

# Install net-tools
sudo apt install net-tools -y

# Create a Postgres user and give it passwordless sudo privileges
sudo adduser postgres
sudo visudo
```
Add the following string at the end of visudo file

```
postgres ALL=(ALL) NOPASSWD:ALL
```
#### For AWS/EC2 
Move to the pg_cirrus node. Switch to the Postgres user. Copy its id_rsa.pub and run the following command on primary, standby1 and standby2 nodes
Switch to the Postgres user
```
sudo su postgres
```
Place id_rsa.pub to authorized_keys
```
mkdir -p ~/.ssh && echo '<$PG_CIRRUS_NODE_ID_RSA.PUB>' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```
**NOTE**
On AWS/EC2, update the inbound rule for the primary, standby1 and standby2 node to allow All **ICMP - IPv4 traffic** from the pg_cirrus node.
We need to open the PostgreSQL port (default is 5432 or the port on which the server is being installed) on primary to allow standby1 and standby2 to establish replication.

### Configure pg_cirrus Node

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

# Install net-tools
sudo apt install net-tools -y

# Create a Postgres user and give it passwordless sudo privileges
sudo adduser postgres
sudo visudo
```
Add the following string at the end of visudo file

```
postgres ALL=(ALL) NOPASSWD:ALL
```
Switch to Postgres user
```
sudo su postgres 
```
Generate SSH key-pair if key-pair is not already generated

**NOTE**: If you have already generated the public key of the Postgres user you may skip this step

```
ssh-keygen -t rsa
```
Copy the public key of the Postgres user on pg_cirrus host to standby1, standby2, and primary hosts for SSH passwordless access (For AWS/EC2 refer to the above Configure Primary, Standby1, and Standby2 Nodes section)

```
ssh-copy-id postgres@<PRIMARY_IP>
ssh-copy-id postgres@<STANDBY1_IP>
ssh-copy-id postgres@<STANDBY2_IP>
```
Copy the public key of the Postgres user to authorized_keys inside the Postgres user
```
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

Clone GitHub repository

```
git clone https://github.com/stormatics/pg_cirrus
```
Go into the directory 

```
cd pg_cirrus/3-node-cluster/
```
 
Create a vault.yml file using Ansible vault

```
ansible-vault create vault.yml
```
You will be prompted for vault password, after entering vault password vault file will be open.

Write the following lines inside vault.yml

```
PSQL_SERVER_PASSWORD: <your_psql_server_password>
REPUSER_PASSWORD: <your_replication_user_password>
```

Create a file to store the vault password
```
touch <file_name>
chmod 0600 <file_name>
```
Write the vault password inside this file

### Execute pg_cirrus
```
python3 deploy.py
```
