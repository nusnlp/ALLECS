#!/bin/bash

COMBINATION_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MEMT=$(dirname "$(dirname "$COMBINATION_PATH")")
MEMT_PORT_NUMBER=1994

export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MEMT/memt/install/boost_1_49_0/stage/lib"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MEMT/memt/install/icu/source/lib"

$MEMT/memt/MEMT/scripts/server.sh --lm.file $MEMT/memt/wiki+nucle.arpa --port ${1:-$MEMT_PORT_NUMBER}
