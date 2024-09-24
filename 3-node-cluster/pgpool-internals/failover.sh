#!/bin/bash

# failover.sh
# This script gets executed by failover_command parameter used by pgpool.conf file. This script will promote a standby server to primary in case of failover.

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
# 13) PG_MAJOR_VERSION = major version number of PostgreSQL server
# 14) %% = '%' character

# Assigning values to variables.
FAILED_NODE_ID="$1"
FAILED_NODE_HOST="$2"
FAILED_NODE_PORT="$3"
FAILED_NODE_PGDATA="$4"
NEW_MAIN_NODE_ID="$5"
NEW_MAIN_NODE_HOST="$6"
OLD_MAIN_NODE_ID="$7"
OLD_PRIMARY_NODE_ID="$8"
NEW_MAIN_NODE_PORT="$9"
NEW_MAIN_NODE_PGDATA="${10}"
OLD_PRIMARY_NODE_HOST="${11}"
OLD_PRIMARY_NODE_PORT="${12}"
PG_MAJOR_VERSION="${13}"
PG_PORT="${14}"

# Promoting standby node as new primary node.
if [ -f /etc/redhat-release ]; then
	ssh postgres@$NEW_MAIN_NODE_HOST "/usr/pgsql-$PG_MAJOR_VERSION/bin/pg_ctl -D $NEW_MAIN_NODE_PGDATA -o '-p $PG_PORT' promote"
else
	ssh postgres@$NEW_MAIN_NODE_HOST "/usr/lib/postgresql/$PG_MAJOR_VERSION/bin/pg_ctl -D $NEW_MAIN_NODE_PGDATA -o '-p $PG_PORT' promote"
fi
