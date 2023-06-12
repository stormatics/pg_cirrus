import subprocess

def _GENERATE_INVENTORY_FILE(PRIMARY_SSH_USERNAME, PRIMARY_IP):
  print("Generating inventory file ...")

  with open('inventory', 'w') as file:
    file.write("PRIMARY ansible_host="+ PRIMARY_IP +" ansible_connection=ssh ansible_user="+ PRIMARY_SSH_USERNAME)

def _GENERATE_CONF_FILE(PRIMARY_PORT, POSTGRESQL_VERSION, PG_CIRRUS_INSTALLATION_DIRECTORY):
    print("Generating common file ...")
    with open('var_file.yml', 'w') as file:
      file.write('PRIMARY_PORT: ' + PRIMARY_PORT + '\n')
      file.write('POSTGRESQL_VERSION: ' + POSTGRESQL_VERSION + '\n')
      file.write('PG_CIRRUS_INSTALLATION_DIRECTORY: ' + PG_CIRRUS_INSTALLATION_DIRECTORY)

def _EXECUTE_PLAYBOOK():
    subprocess.run(['ansible-playbook', '-e', "@/home/semab/pg_cirrus/3-node-cluster/var_file.yml", "-i", "inventory", "ansible/setup-primary.yml"])

def main():
  print("Hello World! This is pg_cirrus\n\n")

  print("1: Setup 3 node cluster")
  print("2: Add Standby with Primary")
  USER_CHOICE = input("Please enter your choice: ")

  if int(USER_CHOICE) == 1:
    print("Setting up 3 node cluster")

    print("Please enter required information for Primary server: ")
    PRIMARY_SSH_USERNAME = input("Username to establish ssh connection: ")
    PRIMARY_IP = input("IP address: ")
    PRIMARY_PORT = input("PostgreSQL port: ")
    POSTGRESQL_VERSION = input("PostgreSQL version: ")
    PG_CIRRUS_INSTALLATION_DIRECTORY = input("pg_cirrus configuration directory: ")

    _GENERATE_CONF_FILE(PRIMARY_PORT, POSTGRESQL_VERSION, PG_CIRRUS_INSTALLATION_DIRECTORY)
    _GENERATE_INVENTORY_FILE(PRIMARY_SSH_USERNAME, PRIMARY_IP)

    _EXECUTE_PLAYBOOK()

  elif int(USER_CHOICE) == 2:
    print("Adding Standby with Primary")
  else:
    print("Invalid choice")

if __name__ == "__main__":
  main()
