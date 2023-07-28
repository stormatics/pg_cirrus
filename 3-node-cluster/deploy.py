# This is the main python file to execute pg_cirrus

# Importing required python libraries
import subprocess
import os
import getpass
import stat
import pwd
import sys

# Function to execute setup-pgdg-repo.yml playbook on localhost
def EXECUTE_PGDG_PLAYBOOK():
    subprocess.run(['ansible-playbook', 'ansible/playbooks/setup-pgdg-repo.yml'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Function to execute setup-primary.yml playbook on primary server
def EXECUTE_PRIMARY_PLAYBOOK(VAULT_PASSWORD_FILE):
    try:
        subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-primary.yml", "--vault-password-file="+ VAULT_PASSWORD_FILE], check=True)
    except subprocess.CalledProcessError as ERROR:
        print("Error: Failed to execute setup-primary.yml playbook.")
        raise ERROR

# Function to execute setup-standby.yml playbook on standby servers
def EXECUTE_STANDBY_PLAYBOOK(VAULT_PASSWORD_FILE):
    try:
        subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-standby.yml", "--vault-password-file="+ VAULT_PASSWORD_FILE], check=True)
    except subprocess.CalledProcessError as ERROR:
        print("Error: Failed to execute setup-standby.yml playbook.")
        raise ERROR

# Function to execute setup-pgpool.yml playbook on localhost
def EXECUTE_PGPOOL_PLAYBOOK(VAULT_PASSWORD_FILE):
    try:
        subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-pgpool.yml", "--vault-password-file="+ VAULT_PASSWORD_FILE], check=True)
    except subprocess.CalledProcessError as ERROR:
        print("Error: Failed to execute setup-pgpool.yml playbook.")
        raise ERROR

# Function to generate inventory file at runtime
def GENERATE_INVENTORY_FILE(PRIMARY_IP, STANDBY_SERVERS):
    print("Generating inventory file ...")

    with open('inventory', 'w') as file:
        file.write("PRIMARY ansible_host=" + PRIMARY_IP + " ansible_connection=ssh ansible_user=postgres\n")
        file.write("[STANDBY]\n")
        for i, SERVER in enumerate(STANDBY_SERVERS, start=1):
            file.write("STANDBY" + str(i) + " ansible_host=" + SERVER['IP'] + " ansible_connection=ssh ansible_user=postgres\n")

# Function to generate variable file at runtime
def GENERATE_VAR_FILE(PG_PORT, PG_VERSION, PG_CIRRUS_INSTALLATION_DIRECTORY, CLUSTER_SUBNET, STANDBY_SERVERS):
    print("Generating conf.yml ...")
    with open('conf.yml', 'w') as file:
        file.write('PG_PORT: ' + PG_PORT + '\n')
        file.write('PG_VERSION: ' + PG_VERSION + '\n')
        file.write('PG_CIRRUS_INSTALLATION_DIRECTORY: ' + PG_CIRRUS_INSTALLATION_DIRECTORY + '\n')
        file.write('CLUSTER_SUBNET: '+ CLUSTER_SUBNET +'\n')
        file.write('STANDBY_SERVERS:\n')
        for i, SERVER in enumerate(STANDBY_SERVERS, start=1):
            file.write('  - NAME: STANDBY' + str(i) + '\n')
            file.write('    PG_REPLICATION_SLOT: ' + SERVER['REPLICATION_SLOT'] + '\n')

# Function to get latest PostgreSQL major version
def GET_LATEST_POSTGRESQL_MAJOR_VERSION():

    EXECUTE_PGDG_PLAYBOOK()

    # Get the latest major version number
    OUTPUT = os.popen('sudo apt-cache policy postgresql').read()

    # Extract the latest major version number
    MAJOR_VERSION = next(line.split(':')[1].strip().split('.')[0] for line in OUTPUT.split('\n') if 'Candidate' in line)
    MAJOR_VERSION = MAJOR_VERSION.split('+')[0]  # Extract only the major number

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
    USER_PORT = input(f"Enter the PostgreSQL port number: (Default: {DEFAULT_PORT}): ")

    if USER_PORT:
        return str(USER_PORT)
    else:
        return str(DEFAULT_PORT)

# Function to set the path of data directory. If user enters a path that path is set as PG_CIRRUS_INSTALLATION_DIRECTORY, if user doesn't enter a path default "/home/postgres/stormatics/pg_cirrus/data" path is used.
def GET_DATA_DIRECTORY_PATH():
    DEFAULT_PATH = "/home/postgres/stormatics/pg_cirrus/data"
    USER_PATH = input(f"Enter the Data Directory Path: (Default: {DEFAULT_PATH}): ")

    if USER_PATH:
        return USER_PATH
    else:
        return DEFAULT_PATH

# Function to check if VAULT_PASSWORD_FILE exists and if it exists, does it have permission 0600.
def CHECK_VAULT_PASSWORD_FILE(FILE_PATH):
    # Check if file exists
    if not os.path.exists(FILE_PATH):
        print(f"File '{FILE_PATH}' does not exist.")
        return False

    # Check file permissions
    file_permissions = stat.S_IMODE(os.lstat(FILE_PATH).st_mode)
    if file_permissions != 0o600:
        print(f"File '{FILE_PATH}' does not have the correct permissions (0600).")
        return False

    # All conditions passed
    return True

# Function to execute all playbooks
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

# MAIN FUNCTION
def main():
  print("Welcome to pg_cirrus - Hassle-free PostgreSQL Cluster Setup\n\n")

  VAULT_PASSWORD_FILE = input("Ansible vault password file: ")
  # Call the function to check file conditions
  if CHECK_VAULT_PASSWORD_FILE(VAULT_PASSWORD_FILE):
    print("All checks for VAULT_PASSWORD_FILE were passed")
  else:
    print("Few security checks for VAULT_PASSWORD_FILE failed please refer to documentation for more details")
    exit(1)

  print("\n")
  print("Getting latest PostgreSQL stable version ...")
  PG_VERSION = GET_POSTGRESQL_VERSION()

  print("\n")
  PG_PORT = GET_POSTGRESQL_PORT()

  print("\n")
  PG_CIRRUS_INSTALLATION_DIRECTORY = GET_DATA_DIRECTORY_PATH()

  print("\n")
  PRIMARY_IP = input("Primary PostgreSQL Server IP address: ")

  print("\n")
  STANDBY_COUNT = 2
  STANDBY_SERVERS = []
  for i in range(1, STANDBY_COUNT + 1):
    STANDBY_IP = input("Standby "+ str(i) +" IP address: ")
    REPLICATION_SLOT = STANDBY_IP.replace(".", "_")
    STANDBY_SERVERS.append({'IP': STANDBY_IP, 'REPLICATION_SLOT': "slot_"+ REPLICATION_SLOT})

  CLUSTER_SUBNET = input("\n\nSubnet address for the cluster: ")

  GENERATE_VAR_FILE(PG_PORT, PG_VERSION, PG_CIRRUS_INSTALLATION_DIRECTORY, CLUSTER_SUBNET, STANDBY_SERVERS)
  GENERATE_INVENTORY_FILE(PRIMARY_IP, STANDBY_SERVERS)

  EXECUTE_PLAYBOOKS(VAULT_PASSWORD_FILE)

if __name__ == "__main__":
  main()

