# highly-available-cluster

This directory contains script files to setting up 3-Node highly available PostgreSQL cluster.

## Prerequisites

### Configure Primary, Standby1 and Standby2 Nodes

Install OpenSSH Server
* sudo apt-get install openssh-server -y

Create postgres user and give it sudo privileges
* sudo adduser postgres
* sudo usermod -aG sudo postgres

### Configure Pgpool Node

Install OpenSSH Server
* sudo apt-get install openssh-server -y

Install Ansible
* sudo apt-get install ansible -y

Install Git
* sudo apt-get install git -y

Copy pgpool host’s root public key to primary, Stancby1 and Standby2 nodes for ssh passwordless access

**NOTE**: If you have already generated public key of root user you may skip first 2 steps and move to 3rd step
* sudo su -
* ssh-keygen 
* ssh-copy-id postgres@$PRIMARY_IP
* ssh-copy-id postgres@$STANDBY1_IP
* ssh-copy-id postgres@$STANDBY2_IP

Clone github repository
* git clone https://github.com/stormatics/pg_cirrus
 
### Prepare hosts.yml.in file

* cp hosts.yml.in hosts.yml

**NOTE**: Replace the fields ansible_host and ansible_become with your ip addresses and passwords You can find your ip address on primary, standby1 and standby2 hosts using ifconfig command.

### Run ansible playbook
* sudo ansible-playbook -i hosts.yml setup.yml

Your 3 Node Cluster with failover must now be running smoothly 
