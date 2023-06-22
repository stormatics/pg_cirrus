#!/bin/bash

# follow_primary.sh
# This script is executed by follow_primary_command parameter used by pgpool.conf file. This file gets executed on all standby nodes including new primary node as well.
# We are updating replication properties from all standby nodes to the new primary node

set -o xtrace

# Special values:
# 1)  %d = failed node id
# 2)  %h = failed node hostname
# 3)  %p = failed node port number
# 4)  %D = failed node database cluster path
# 5)  %m = new main node id
# 6)  %H = new main node hostname
# 7)  %M = old main node id
# 8)  %P = old primary node id
# 9)  %r = new main port number
# 10) %R = new main database cluster path
# 11) %N = old primary node hostname
# 12) %S = old primary node port number
# 13) %% = '%' character

NODE_ID="$1"
NODE_HOST="$2"
NODE_PORT="$3"
NODE_PGDATA="$4"
NEW_MAIN_NODE_ID="$5"
NEW_MAIN_NODE_HOST="$6"
OLD_MAIN_NODE_ID="$7"
OLD_PRIMARY_NODE_ID="$8"
NEW_MAIN_NODE_PORT="$9"
NEW_MAIN_NODE_PGDATA="${10}"
OLD_PRIMARY_NODE_HOST="${11}"
OLD_PRIMARY_NODE_PORT="${12}"
 
# Check if this script is being executed on newly promoted primary then we don't need to do anything
if [[ "$NODE_HOST" == "$OLD_PRIMARY_NODE_HOST" ]]; then
	echo Nothing to do
	exit 0
fi

# Create a new replication slot on new primary
ssh postgres@$NEW_MAIN_NODE_HOST "echo 123 | psql -d postgres -W -c \"SELECT pg_create_physical_replication_slot('sb2');\""

# Update connection string on all standby nodes to point to new primary
ssh postgres@$NODE_HOST "echo 123 |  psql -d postgres -W -c \"ALTER SYSTEM SET primary_conninfo = 'user=repuser password=repuserpassword channel_binding=prefer host=$NEW_MAIN_NODE_HOST port=5432 sslmode=prefer sslcompression=0 sslsni=1 ssl_min_protocol_version=TLSv1.2 gssencmode=prefer krbsrvname=postgres target_session_attrs=any';\""

# Reload connection properties
ssh postgres@$NODE_HOST "echo 123 | psql -d postgres -W -c \"SELECT pg_reload_conf();\""
