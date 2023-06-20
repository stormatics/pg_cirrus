import subprocess

def _EXECUTE_PRIMARY_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/setup-primary.yml"])

def _EXECUTE_STANDBY_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/setup-standby.yml"])

def _EXECUTE_PGPOOL_PLAYBOOK():
    subprocess.run(['ansible-playbook', "-i", "inventory", "ansible/setup-pgpool.yml"])

def main():
  print("Hello World! This is pg_cirrus\n\n")

  print("Setup 3 node cluster")
  _EXECUTE_PRIMARY_PLAYBOOK()
  _EXECUTE_STANDBY_PLAYBOOK()
  _EXECUTE_PGPOOL_PLAYBOOK()

if __name__ == "__main__":
  main()

