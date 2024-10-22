#!/bin/bash

# init.sh
# This file is used to install pre requirements. Run this file on all the nodes in the cluster

# Function to detect package manager and install required packages
install_packages() {
    if [ -f /etc/redhat-release ]; then
        # Red Hat-based systems (RHEL, CentOS, etc.)
        echo "Detected Red Hat-based system. Installing packages..."
        sudo yum install -y openssh-server net-tools python3 acl ansible
    elif [ -f /etc/debian_version ]; then
        # Debian-based systems (Ubuntu, Debian, etc.)
        echo "Detected Debian-based system. Installing packages..."
        sudo apt-get update -y
        sudo apt-get install -y openssh-server net-tools python3 acl ansible
    else
        echo "Unsupported OS. Exiting."
        exit 1
    fi
}

# Set the postgres password
POSTGRES_PASSWORD="postgres"

# Update package manager cache and install packages
install_packages

# Ensure postgres user is created with default password
echo "Ensuring postgres user is created..."
if id "postgres" &>/dev/null; then
    echo "User postgres already exists"
else
    sudo useradd -m -s /bin/bash postgres
    echo "postgres:$POSTGRES_PASSWORD" | sudo chpasswd
fi

# Allow postgres user to run sudo without a password
echo "Configuring sudoers for postgres..."
if ! sudo grep -q "postgres ALL=(ALL) NOPASSWD:ALL" /etc/sudoers; then
    echo "postgres ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers
    sudo visudo -cf /etc/sudoers
fi

# Ensure SSH directory exists for postgres user
echo "Ensuring SSH directory exists for postgres user..."
sudo mkdir -p /home/postgres/.ssh
sudo chown postgres:postgres /home/postgres/.ssh
sudo chmod 700 /home/postgres/.ssh

# Generate SSH key pair if not already present
echo "Generating SSH key pair for postgres user..."
if [ ! -f /home/postgres/.ssh/id_rsa ]; then
    sudo -u postgres ssh-keygen -t rsa -b 4096 -N "" -f /home/postgres/.ssh/id_rsa
fi

# Ensure correct permissions on generated SSH keys
echo "Setting correct permissions on SSH keys..."
sudo chown postgres:postgres /home/postgres/.ssh/id_rsa
sudo chmod 600 /home/postgres/.ssh/id_rsa

echo "Pre-requisites installation completed."

