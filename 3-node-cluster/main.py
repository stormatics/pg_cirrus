import subprocess

def _EXECUTE_PRIMARY_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/setup-primary.yml"])

def _EXECUTE_STANDBY_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/setup-standby.yml"])

def _EXECUTE_PGPOOL_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/setup-pgpool.yml"])

def generate_inventory_file(primary_ssh_username, primary_ip, standby_servers):
    print("Generating inventory file ...")

    with open('inventory', 'w') as file:
        file.write("PRIMARY ansible_host=" + primary_ip + " ansible_connection=ssh ansible_user=" + primary_ssh_username + "\n")
        file.write("[STANDBY]\n")
        for i, server in enumerate(standby_servers, start=1):
            file.write("STANDBY" + str(i) + " ansible_host=" + server['ip'] + " ansible_connection=ssh ansible_user=" + server['ssh_username'] + "\n")

def generate_var_file(pg_port, pfile_directory, pg_version, pg_cirrus_installation_directory, pg_password, standby_servers):
    print("Generating var_file.yml ...")
    with open('var_file.yml', 'w') as file:
        file.write('PG_PORT: ' + pg_port + '\n')
        file.write('PFILE_DIRECTORY: ' + pfile_directory + '\n')
        file.write('PG_VERSION: ' + pg_version + '\n')
        file.write('PG_CIRRUS_INSTALLATION_DIRECTORY: ' + pg_cirrus_installation_directory + '\n')
        file.write('PG_PASSWORD: ' + pg_password + '\n')
        file.write('STANDBY_SERVERS:\n')
        for i, server in enumerate(standby_servers, start=1):
            file.write('  - name: STANDBY' + str(i) + '\n')
            file.write('    PG_REPLICATION_SLOT: ' + server['replication_slot'] + '\n')

def get_latest_postgresql_major_version():
    # Add the pgdg repo to sources.list.d
    subprocess.run(['sudo', 'sh', '-c', 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Download PostgreSQL key and add it to system keyring
    subprocess.run(['wget', '--quiet', 'https://www.postgresql.org/media/keys/ACCC4CF8.asc'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['sudo', 'apt-key', 'add', 'ACCC4CF8.asc'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Update apt cache
    subprocess.run(['sudo', 'apt', 'update'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Get the latest major version number
    output = subprocess.run(['sudo', 'apt-cache', 'policy', 'postgresql'], capture_output=True, text=True).stdout

    # Extract the latest major version number
    major_version = next(line.split(':')[1].strip().split('.')[0] for line in output.split('\n') if 'Candidate' in line)
    major_version = major_version.split('+')[0]  # Extract only the major number

    return major_version.strip()


def get_postgresql_version():
    latest_version = get_latest_postgresql_major_version()
    user_version = input(f"Enter PostgreSQL version (Latest: {latest_version}): ")
    if user_version.strip():
        return user_version.strip()
    else:
        return latest_version.strip()


def main():
    print("Hello World! This is pg_cirrus\n\n")

    print("1: Setup 3 node cluster")
    print("2: Add Standby with Primary")
    user_choice = input("Please enter your choice: ")

    if int(user_choice) == 1:
        print("Setting up 3 node cluster")

        print("Please enter required information for Primary server: \n")
        primary_ssh_username = input("Username to establish ssh connection: ")
        primary_ip = input("Primary PostgreSQL Server IP address: ")
        pg_port = input("PostgreSQL port: ")
        pfile_directory = input("Pfile directory: ")
        pg_version = get_postgresql_version()
        pg_cirrus_installation_directory = input("pg_cirrus installation directory: ")
        pg_password = input("PostgreSQL password: ")
        print("\n")
        standby_count = 2
        standby_servers = []
        for i in range(1, standby_count + 1):
            print("Please enter required information for Standby", i, "server:")
            standby_ssh_username = input("Username to establish ssh connection: ")
            standby_ip = input("Standby IP address: ")
            replication_slot = input("Replication slot name: ")
            print("\n")
            standby_servers.append({'ip': standby_ip, 'ssh_username': standby_ssh_username, 'replication_slot': replication_slot})

        generate_var_file(pg_port, pfile_directory, pg_version, pg_cirrus_installation_directory, pg_password, standby_servers)
        generate_inventory_file(primary_ssh_username, primary_ip, standby_servers)

        _EXECUTE_PRIMARY_PLAYBOOK()
        _EXECUTE_STANDBY_PLAYBOOK()
        _EXECUTE_PGPOOL_PLAYBOOK()

    elif int(USER_CHOICE) == 2:
      print("Adding Standby with Primary")
    else:
      print("Invalid choice")

if __name__ == "__main__":
    main()

