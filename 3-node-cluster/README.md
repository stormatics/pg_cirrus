# Configure pg_cirrus, Primary, Standby1 and Standby2 Nodes
Download init.sh file from pg_cirrus repository and execute it on all the nodes inside the cluster
- curl -OL https://raw.githubusercontent.com/mahatariq11/pg_cirrus/refs/heads/dev-improving-codebase/3-node-cluster/init.sh
- chmod +x init.sh
- ./init.sh

Open the init.sh file and search for :
- POSTGRES_PASSWORD="*****"

 Replace the password value with your OS postgres user’s password.

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
- Port 9000 should be open for Watchdog communication, which monitors the status of PostgreSQL nodes in the cluster.
- Also open port 22 on all PostgreSQL nodes to allow SSH communication between them.
- Port 9694 must be open on all nodes for Watchdog health check communication between Pgpool-II instances.

# Setup passwordless SSH access between primary and standby

- Copy ~/.ssh/id_rsa.pub file content from primary and paste it into ~/.ssh/authorized_keys file on standby1, standby2, and primary itself
- Copy ~/.ssh/id_rsa.pub file content from standby1 and paste it into ~/.ssh/authorized_keys file on primary, standby2, and standby1 itself
- Copy ~/.ssh/id_rsa.pub file content from standby2 and paste it into ~/.ssh/authorized_keys file on primary, standby1, and standby2 itself

Now, test your SSH connection by attempting to connect to each node from the other nodes
# Copy the public key of the Postgres user to authorized_keys inside the Postgres user on pg_cirrus node

- cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys

# Clone pg_cirrus on pg_cirrus node

Go to $HOME of postgres user
- cd $HOME

Clone pg_cirrus
- git clone https://github.com/mahatariq11/pg_cirrus.git
- cd pg_cirrus/3-node-cluster


# Create a vault.yml file using Ansible vault
The vault.yml file is used to store the database credentials for the cluster.
Navigate to your chosen secure location and execute the following command to create this file:
- ansible-vault create vault.yml

You will be prompted to enter the vault password.
After providing the password, the vault file will open.
Add the following lines to the vault.yml file, update the password as required, and then save the file.

- PSQL_SERVER_PASSWORD: <your_psql_server_password>
- REPUSER_PASSWORD: <your_replication_user_password>
- WATCHDOG_AUTHENTICATION_KEY: <watchdog_communication_password>

# Create a file to store the vault password

- touch vault
- chmod 0600 vault
Write the vault password inside this file


# Execute pg_cirrus

- python3 deploy.py
