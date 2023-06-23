# Importing required python libraries
import subprocess
import os

# Function to execute setu-pgdg-repo.yml playbook on localhost
def EXECUTE_PGDG_PLAYBOOK():
    subprocess.run(['ansible-playbook', "ansible/playbooks/setup-pgdg-repo.yml"])

# Function to execute setup-primary.yml playbook on primary server
def EXECUTE_PRIMARY_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-primary.yml"])

# Function to execute setup-standby.yml playbook on standby servers
def EXECUTE_STANDBY_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-standby.yml"])

# Function to execute setup-pgpool.yml playbook on localhost
def EXECUTE_PGPOOL_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/playbooks/setup-pgpool.yml"])

# Function to generate inventory file at runtime
def GENERATE_INVENTORY_FILE(PRIMARY_SSH_USERNAME, PRIMARY_IP, STANDBY_SERVERS):
    print("Generating inventory file ...")

    with open('inventory', 'w') as file:
        file.write("PRIMARY ansible_host=" + PRIMARY_IP + " ansible_connection=ssh ansible_user=" + PRIMARY_SSH_USERNAME + "\n")
        file.write("[STANDBY]\n")
        for i, SERVER in enumerate(STANDBY_SERVERS, start=1):
            file.write("STANDBY" + str(i) + " ansible_host=" + SERVER['IP'] + " ansible_connection=ssh ansible_user=" + SERVER['SSH_USERNAME'] + "\n")

# Function to generate variable file at runtime
def GENERATE_VAR_FILE(PG_PORT, PFILE_DIRECTORY, PG_VERSION, PG_CIRRUS_INSTALLATION_DIRECTORY, PG_PASSWORD, STANDBY_SERVERS):
    print("Generating var_file.yml ...")
    with open('var_file.yml', 'w') as file:
        file.write('PG_PORT: ' + PG_PORT + '\n')
        file.write('PFILE_DIRECTORY: ' + PFILE_DIRECTORY + '\n')
        file.write('PG_VERSION: ' + PG_VERSION + '\n')
        file.write('PG_CIRRUS_INSTALLATION_DIRECTORY: ' + PG_CIRRUS_INSTALLATION_DIRECTORY + '\n')
        file.write('PG_PASSWORD: ' + PG_PASSWORD + '\n')
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
    USER_VERSION = input(f"Enter PostgreSQL version (Latest: {LATEST_VERSION}): ")
    if USER_VERSION.strip():
        return USER_VERSION.strip()
    else:
        return LATEST_VERSION.strip()

# Main python function
def main():
    print("Hello World! This is pg_cirrus\n\n")

    print("1: Seup 3 node cluster")
    print("2: Add Standby with Primary")
    USER_CHOICE = input("Please enter your choice: ")

    if int(USER_CHOICE) == 1:
        print("Setting up 3 node cluster")

        print("Please enter required information for Primary server: \n")
        PRIMARY_SSH_USERNAME = input("Username to establish ssh connection: ")
        PRIMARY_IP = input("Primary PostgreSQL Server IP address: ")
        PG_PORT = input("PostgreSQL port: ")
        PFILE_DIRECTORY = input("Pfile directory: ")
        PG_VERSION = GET_POSTGRESQL_VERSION()
        PG_CIRRUS_INSTALLATION_DIRECTORY = input("pg_cirrus installation directory: ")
        PG_PASSWORD = input("PostgreSQL password: ")
        print("\n")
        STANDBY_COUNT = 2
        STANDBY_SERVERS = []
        for i in range(1, STANDBY_COUNT + 1):
            print("Please enter required information for Standby", i, "server:")
            STANDBY_SSH_USERNAME = input("Username to establish ssh connection: ")
            STANDBY_IP = input("Standby IP address: ")
            REPLICATION_SLOT = input("Replication slot name: ")
            print("\n")
            STANDBY_SERVERS.append({'IP': STANDBY_IP, 'SSH_USERNAME': STANDBY_SSH_USERNAME, 'REPLICATION_SLOT': REPLICATION_SLOT})

        GENERATE_VAR_FILE(PG_PORT, PFILE_DIRECTORY, PG_VERSION, PG_CIRRUS_INSTALLATION_DIRECTORY, PG_PASSWORD, STANDBY_SERVERS)
        GENERATE_INVENTORY_FILE(PRIMARY_SSH_USERNAME, PRIMARY_IP, STANDBY_SERVERS)

        EXECUTE_PRIMARY_PLAYBOOK()
        EXECUTE_STANDBY_PLAYBOOK()
        EXECUTE_PGPOOL_PLAYBOOK()

    elif int(USER_CHOICE) == 2:
      print("Adding Standby with Primary")
    else:
      print("Invalid choice")

if __name__ == "__main__":
    main()

