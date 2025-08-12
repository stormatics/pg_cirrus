# deploy.py
# This is the main python file to execute pg_cirrus.

# Importing required python libraries.
import json
import subprocess
import os
import getpass
import stat
import pwd
import ipaddress
import sys

class DualLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", buffering=1)  # Line-buffered

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = sys.stderr = DualLogger("cluster-logs.log")

CONFIG_FILE = "cluster-config.json"
def LOAD_CONFIG():
    """Load saved config from disk, or return None if it doesn't exist."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def SAVE_CONFIG(config):
    """Save config dictionary to disk."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Function to execute setup-pgdg-repo.yml playbook on localhost.
def EXECUTE_PGDG_PLAYBOOK():
    try:
        process = subprocess.Popen(
            ['ansible-playbook', 'ansible/playbooks/setup-pgdg-repo.yml'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(line, end='')
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
    except subprocess.CalledProcessError:
        print("Error: Failed to execute setup-pgdg-repo.yml playbook.")

# Function to execute setup-primary.yml playbook on primary server.
def EXECUTE_PRIMARY_PLAYBOOK(VAULT_PASSWORD_FILE):
    try:
        process = subprocess.Popen(
            ['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-primary.yml", "--vault-password-file=" + VAULT_PASSWORD_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(line, end='')
        process.wait()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
    except subprocess.CalledProcessError as ERROR:
        print("Error: Failed to execute setup-primary.yml playbook.")
        raise ERROR

# Function to execute setup-standby.yml playbook on standby servers.
def EXECUTE_STANDBY_PLAYBOOK(VAULT_PASSWORD_FILE):
    try:
        process = subprocess.Popen(
            ['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-standby.yml", "--vault-password-file=" + VAULT_PASSWORD_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(line, end='')
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
    except subprocess.CalledProcessError:
        print("Error: Failed to execute setup-standby.yml playbook.")
        raise

# Function to execute setup-pgpool.yml playbook on localhost.
def EXECUTE_PGPOOL_PLAYBOOK(VAULT_PASSWORD_FILE):
    try:
        process = subprocess.Popen(
            ['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-pgpool.yml", "--vault-password-file=" + VAULT_PASSWORD_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(line, end='')
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
    except subprocess.CalledProcessError:
        print("Error: Failed to execute setup-pgpool.yml playbook.")
        raise

# Function to generate inventory file at runtime.
def GENERATE_INVENTORY_FILE(PRIMARY_IP, STANDBY_SERVERS):
    print("Generating inventory file ...")

    with open('inventory', 'w') as file:
        file.write("PRIMARY ansible_host=" + PRIMARY_IP + " ansible_connection=ssh ansible_user=postgres\n")
        file.write("[STANDBY]\n")
        for i, SERVER in enumerate(STANDBY_SERVERS, start=1):
            file.write("STANDBY" + str(i) + " ansible_host=" + SERVER['IP'] + " ansible_connection=ssh ansible_user=postgres\n")

# Function to generate variable file at runtime.
def GENERATE_VAR_FILE(PG_PORT, PG_VERSION, INITDB_PATH, CLUSTER_SUBNET, STANDBY_SERVERS, PGPOOL_IP, DELEGATE_IP):
    print("Generating conf.yml ...")
    with open('conf.yml', 'w') as file:
        file.write('PG_PORT: ' + PG_PORT + '\n')
        file.write('PG_VERSION: ' + PG_VERSION + '\n')
        file.write('PGPOOL_IP: ' + PGPOOL_IP + '\n')
        file.write('INITDB_PATH: ' + INITDB_PATH + '\n')
        file.write('CLUSTER_SUBNET: '+ CLUSTER_SUBNET +'\n')
        file.write('DELEGATE_IP: ' + DELEGATE_IP + '\n')
        file.write('STANDBY_SERVERS:\n')
        for i, SERVER in enumerate(STANDBY_SERVERS, start=1):
            file.write('  - NAME: STANDBY' + str(i) + '\n')
            file.write('    PG_REPLICATION_SLOT: ' + SERVER['REPLICATION_SLOT'] + '\n')

# Function to get latest PostgreSQL major version.
def GET_LATEST_POSTGRESQL_MAJOR_VERSION():

    EXECUTE_PGDG_PLAYBOOK()

    # Get the latest major version number.
    if os.path.exists('/usr/bin/apt'):
        OUTPUT = os.popen('sudo apt-cache policy postgresql').read()
        # Extract the latest major version number.
        MAJOR_VERSION = next(line.split(':')[1].strip().split('.')[0] for line in OUTPUT.split('\n') if 'Candidate' in line)
        MAJOR_VERSION = MAJOR_VERSION.split('+')[0]  # Extract only the major number.

    if os.path.exists('/usr/bin/yum'):
        try:
            subprocess.run(['ansible-playbook', "--become", "ansible/playbooks/setup-pgdg-repo.yml"], check=True)
        except subprocess.CalledProcessError as ERROR:
            print("Error: Failed to execute setup-pgdg-repo.yml playbook.")
            raise ERROR
        MAJOR_VERSION = os.popen("sudo yum info postgresql*-server | grep Version | awk '{print $3}' | cut -d '.' -f 1 | sort -V | tail -n 1").read()

    return MAJOR_VERSION.strip()

# Function to set the value of PostgreSQL version to install. If user clicks enter latest will be selected. If user enters a number that version will be installed.
def GET_POSTGRESQL_VERSION():
    LATEST_VERSION = GET_LATEST_POSTGRESQL_MAJOR_VERSION()
    MINIMUM_SUPPORTED_VERSION = 13
    INVALID_INPUTS = 0
    while True:
        USER_VERSION = input(f"Enter PostgreSQL version (Latest: { LATEST_VERSION }): ")

        if USER_VERSION.strip():
            try:
                if not USER_VERSION.isdigit():
                    raise ValueError("Invalid input: Version should be a number.")
                if int(USER_VERSION) < MINIMUM_SUPPORTED_VERSION:
                    raise ValueError(f"Invalid input: Version cannot be lesser than minimum supported version { MINIMUM_SUPPORTED_VERSION }.")
                if int(USER_VERSION) > int(LATEST_VERSION):
                    raise ValueError(f"Invalid input: Version cannot be greater than latest available version { LATEST_VERSION }.")
            except ValueError as ERROR:
                print(ERROR)
                INVALID_INPUTS += 1
                if INVALID_INPUTS >= 3:
                    print("Too many invalid inputs. Exiting the pg_cirrus.")
                    exit()
            else:
                return USER_VERSION.strip()
        else:
            return LATEST_VERSION.strip()

# Function to set the value of PostgreSQL port. If user enters a value that value is set as PG_PORT, if user doesn't enter a value default 5432 port is used.
def GET_POSTGRESQL_PORT():
    DEFAULT_PORT = 5432
    INVALID_INPUTS = 0
    MINIMUM_PORT = 1
    MAXIMUM_PORT = 65535
    while True:
        USER_PORT = input(f"Enter the PostgreSQL port number: (Default: {DEFAULT_PORT}): ")

        if USER_PORT:
            try:
                if not USER_PORT.isdigit():
                    raise ValueError("Invalid input: Port should be a number.")
                if int(USER_PORT) < MINIMUM_PORT:
                    raise ValueError(f"Invalid input: Port number cannot be lesser than { MINIMUM_PORT }.")
                if int(USER_PORT) > MAXIMUM_PORT:
                    raise ValueError(f"Invalid input: Port number be greater than { MAXIMUM_PORT }.")
            except ValueError as ERROR:
                print(ERROR)
                INVALID_INPUTS += 1
                if INVALID_INPUTS >= 3:
                    print("Too many invalid inputs. Exiting the pg_cirrus.")
                    exit()
            else:
                return str(USER_PORT)
        else:
            return str(DEFAULT_PORT)

# Function to set the path of data directory. If user enters a path that path is set as INITDB_PATH, if user doesn't enter a path default "/home/postgres/stormatics/pg_cirrus/data" path is used.
def GET_DATA_DIRECTORY_PATH():
    DEFAULT_PATH = "/home/postgres/stormatics/pg_cirrus/data"
    USER_PATH = input(f"Enter the Data Directory Path: (Default: {DEFAULT_PATH}): ")

    if USER_PATH:
        return USER_PATH
    else:
        return DEFAULT_PATH

# Function to check if VAULT_PASSWORD_FILE exists and if it exists, does it have permission 0600.
def GET_VAULT_PASSWORD_FILE():
    INVALID_INPUTS = 0
    while True:
        VAULT_PASSWORD_FILE = input(f"Ansible vault password file: ")
        try:
            # Check if file exists.
            if not os.path.exists(VAULT_PASSWORD_FILE):
                raise ValueError(f"File '{VAULT_PASSWORD_FILE}' does not exist.")
        except ValueError as ERROR:
            print(ERROR)
            INVALID_INPUTS += 1
            if INVALID_INPUTS >= 3:
                print("Too many invalid inputs. Exiting the pg_cirrus.")
                exit()
        else:
        # Check file permissions.
            FILE_PERMISSIONS = stat.S_IMODE(os.lstat(VAULT_PASSWORD_FILE).st_mode)
            if FILE_PERMISSIONS != 0o600:
                print(f"File '{VAULT_PASSWORD_FILE}' does not have the correct permissions (0600).")
                exit()
            else:
                print("All checks for VAULT_PASSWORD_FILE were passed")
                return VAULT_PASSWORD_FILE.strip()

# Function to execute all playbooks.
def EXECUTE_PLAYBOOKS(VAULT_PASSWORD_FILE):
    try:
        EXECUTE_PRIMARY_PLAYBOOK(VAULT_PASSWORD_FILE)
        EXECUTE_STANDBY_PLAYBOOK(VAULT_PASSWORD_FILE)
        EXECUTE_PGPOOL_PLAYBOOK(VAULT_PASSWORD_FILE)
    except KeyboardInterrupt:
        print("\npg_cirrus terminated by the user.")
        exit()
    except subprocess.CalledProcessError:
        print("Exiting pg_cirrus.")
        exit()
    except Exception as ERROR:
        print("An unexpected error occurred. Exiting pg_cirrus.", ERROR)
        exit()

# Function to input only valid IP addresses.
def GET_VALID_IP(PROMPT, SUBNET, EXISTING_IPS=[]):
    INVALID_INPUTS = 0

    while True:
        IP = input(PROMPT)
        if not IP:
            print("Empty input. Please enter a valid IP address.")
            INVALID_INPUTS += 1
            if INVALID_INPUTS >= 3:
                print("Too many invalid inputs. Exiting pg_cirrus.")
                exit()
            continue
        try:
            IP_OBJECT = ipaddress.ip_address(IP)
            if IP_OBJECT not in ipaddress.ip_network(SUBNET):
                raise ValueError("Invalid IP address or not within the cluster subnet.")
            if IP in [SERVER['IP'] for SERVER in EXISTING_IPS]:
                raise ValueError("IP address is already added as a Primary or Standby node.")
            if not subprocess.call(['ping', '-c', '1', str(IP)], stdout=subprocess.DEVNULL) == 0:
                raise ValueError("Node is not reachable. Please check the IP address or node availability.")
        except ValueError as ERROR:
            print(ERROR)
            INVALID_INPUTS += 1
            if INVALID_INPUTS >= 3:
                print("Too many invalid inputs. Exiting pg_cirrus.")
                exit()
        else:
            return IP

# Function to input only valid subnet address.
def GET_VALID_SUBNET():
    INVALID_INPUTS = 0
    while True:
        SUBNET = input("Subnet address for the cluster: ")
        if not SUBNET:
            print("Empty input. Please enter a valid subnet address.")
            INVALID_INPUTS += 1
            if INVALID_INPUTS >= 3:
                print("Too many invalid inputs. Exiting pg_cirrus.")
                exit()
            continue
        try:
            ipaddress.ip_network(SUBNET)
            return SUBNET
        except ValueError:
            print("Invalid subnet address.")
            INVALID_INPUTS += 1
            if INVALID_INPUTS >= 3:
                print("Too many invalid inputs. Exiting pg_cirrus.")
                exit()

# Main function to execute pg_cirrus.
def main():
    print("Welcome to pg_cirrus - Hassle-free PostgreSQL Cluster Setup\n\n")

    standby_ips = []  #  Make sure standby_ips is always defined
    config = LOAD_CONFIG()

    if not config:
        # Collect inputs
        vault_password_file = GET_VAULT_PASSWORD_FILE()
        print()
        cluster_subnet = GET_VALID_SUBNET()
        print()
        primary_ip = GET_VALID_IP("Primary PostgreSQL Server IP address: ", cluster_subnet)
        print()
        standby1_ip = GET_VALID_IP("Standby 1 IP address: ", cluster_subnet, [{'IP': primary_ip}])
        print()
        standby2_ip = GET_VALID_IP("Standby 2 IP address: ", cluster_subnet,
                                   [{'IP': primary_ip}, {'IP': standby1_ip}])
        print()
        pgpool_ip = GET_VALID_IP("IP address of this node to setup pgpool: ", cluster_subnet,
                                 [{'IP': primary_ip}, {'IP': standby1_ip}, {'IP': standby2_ip}])
        print()
        delegate_ip = GET_VALID_IP("Enter Delegate IP for Pgpool VIP: ", cluster_subnet,
                           [{'IP': primary_ip}, {'IP': standby1_ip}, {'IP': standby2_ip}, {'IP': pgpool_ip}])
        print()

        standby_ips = [standby1_ip, standby2_ip]  #  Assign list here

        config = {
            "vault_password_file": vault_password_file,
            "cluster_subnet": cluster_subnet,
            "primary_ip": primary_ip,
            "standby_ips": standby_ips,
            "pgpool_ip": pgpool_ip,
            "delegate_ip": delegate_ip
        }
        SAVE_CONFIG(config)
        print("\n Configuration saved to", CONFIG_FILE, "\n")
    else:
        print(" Loaded configuration from", CONFIG_FILE)
        print(json.dumps(config, indent=4), "\n")
        vault_password_file = config["vault_password_file"]
        cluster_subnet = config["cluster_subnet"]
        primary_ip = config["primary_ip"]
        standby_ips = config["standby_ips"]  # Still defined properly
        pgpool_ip = config["pgpool_ip"]
        delegate_ip = config["delegate_ip"]


    # Gather remaining required values
    PG_VERSION = GET_POSTGRESQL_VERSION()
    PG_PORT = GET_POSTGRESQL_PORT()
    INITDB_PATH = GET_DATA_DIRECTORY_PATH()

    # Build standby server structures
    STANDBY_SERVERS = []
    for ip in standby_ips:
        REPLICATION_SLOT = "slot_" + ip.replace(".", "_")
        STANDBY_SERVERS.append({"IP": ip, "REPLICATION_SLOT": REPLICATION_SLOT})

    # Generate necessary files
    GENERATE_VAR_FILE(PG_PORT, PG_VERSION, INITDB_PATH,
                      cluster_subnet, STANDBY_SERVERS, pgpool_ip, delegate_ip)
    GENERATE_INVENTORY_FILE(primary_ip, STANDBY_SERVERS)

    # Run the playbooks
    EXECUTE_PLAYBOOKS(vault_password_file)

if __name__ == "__main__":
    main()

