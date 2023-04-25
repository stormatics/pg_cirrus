# Steps to follow:

## On Primary, Standby1 and Standby2 Hosts
Create postgres user and give it sudo privileges 
sudo adduser postgres
sudo usermod -aG sudo postgres

## On Pgpool Machine

## Clone github repository
sudo su -
git clone - https://<username>:<token>@github.com/stormatics/pg_cirrus.git

## Generate SSH key pair
Copy pgpool host’s root key to standby1, standby2 and primary for ssh passwordless access
sudo su -
ssh-keygen 
ssh-copy-id postgres@$PRIMARY_IP
ssh-copy-id postgres@$SB1_IP
ssh-copy-id postgres@$SB2_IP
 
## Rename hosts.yml.in file to hosts.yml and update

mv hosts.yml.in host.yml  

## Edit hosts.yml file
PG_PRIMARY_HOST ansible_host=xxx.xxx.xxx.xxx ansible_connection=ssh ansible_user=postgres ansible_become_pass=xxxxxxxx
PG_SB1_HOST ansible_host=xxx.xxx.xxx.xxx ansible_connection=ssh ansible_user=postgres ansible_become_pass=xxxxxxxx
PG_SB2_HOST ansible_host=xxx.xxx.xxx.xxx ansible_connection=ssh ansible_user=postgres ansible_become_pass=xxxxxxxx


### Replace the fields in bold with your ip addresses and passwords
PG_PRIMARY_HOST stands for Primary Node
PG_SB1_HOST stands for Standby 1 Node
PG_SB2_HOST stands for Standby 2 Node

You can find your ip address on primary, standby1 and standby2 machines using ifconfig command.

## Run ansible playbook
sudo ansible-playbook -i hosts.yml setup.yml

Your 3 Node Cluster with failover must now be running smoothly 

