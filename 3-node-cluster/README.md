# Configure pg_cirrus, Primary, Standby1 and Standby2 Nodes

Download init.sh file from pg_cirrus repository and execute it on all the nodes inside the cluster
- curl -OL https://raw.githubusercontent.com/stormatics/pg_cirrus/main/3-node-cluster/init.sh
- chmod +x init.sh
- ./init.sh

# Setup passwordless SSH access from pg_cirrus node to other nodes 

Switch to the Postgres user on all the nodes inside the cluster
- sudo su postgres

Copy ~/.ssh/id_rsa.pub file content from pg_cirrus node and run the following command on primary, standby1 and standby2 nodes
- mkdir -p ~/.ssh && echo '<$PG_CIRRUS_NODE_ID_RSA.PUB>' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys

Finally test your SSH connection by connecting to each node from pg_cirrus node

**NOTE**
- On AWS/EC2, update the inbound rule for the primary, standby1 and standby2 node to allow All ICMP - IPv4 traffic from the pg_cirrus node.
- We need to open the PostgreSQL port (default is 5432 or the port on which the server is being installed) on primary to allow standby1 and standby2 to establish replication.
- We also need to open access from pg_cirrus node to all primary, standby1 and standby2 nodes on PostgreSQL port
- Make sure Port 9999 is open on pg_cirrus node to allow any traffic from internet. Because this is the port where Application will be connected

# Copy the public key of the Postgres user to authorized_keys inside the Postgres user on pg_cirrus node

- cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys


# Clone pg_cirrus on pg_cirrus node

Go to $HOME of postgres user
- cd $HOME

Clone pg_cirrus
- git clone https://github.com/stormatics/pg_cirrus.git
- cd pg_cirrus/3-node-cluster


# Create a vault.yml file using Ansible vault

- ansible-vault create vault.yml

You will be prompted for vault password, after entering vault password vault file will be open.

Write the following lines inside vault.yml

PSQL_SERVER_PASSWORD: <your_psql_server_password>

REPUSER_PASSWORD: <your_replication_user_password>


# Create a file to store the vault password

- touch vault
- chmod 0600 vault
Write the vault password inside this file


# Execute pg_cirrus

- python3 deploy.py
