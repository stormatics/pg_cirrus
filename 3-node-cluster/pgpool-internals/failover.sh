#!/bin/bash

set -o xtrace

# Arguments from pgpool
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

# QUORUM CHECK
# Count number of healthy nodes (status = up)
# Assumes PCP port is 9898 and user is postgres with passwordless access via .pcppass

ALIVE_NODES=$(pcp_node_info -h localhost -p 9898 -U postgres -w | grep -c "up")

if [ "$ALIVE_NODES" -lt 2 ]; then
    echo "ERROR: Not enough alive nodes to form quorum (only $ALIVE_NODES). Aborting failover."
    exit 1
fi

# Promote standby node as new primary
if [ -f /etc/redhat-release ]; then
    ssh postgres@$NEW_MAIN_NODE_HOST "/usr/pgsql-$PG_MAJOR_VERSION/bin/pg_ctl -D $NEW_MAIN_NODE_PGDATA -o '-p $PG_PORT' promote"
else
    ssh postgres@$NEW_MAIN_NODE_HOST "/usr/lib/postgresql/$PG_MAJOR_VERSION/bin/pg_ctl -D $NEW_MAIN_NODE_PGDATA -o '-p $PG_PORT' promote"
fi

