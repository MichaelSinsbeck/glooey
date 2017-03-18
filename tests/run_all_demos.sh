#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
BOLD='\033[1;37m'
NORMAL='\033[0m'

for demo in **/demo_*.py; do
    [ -x $demo ] && (
        echo -e $BOLD$demo$NORMAL
        cd $(dirname $demo)
        python $(basename $demo)
    )
done
