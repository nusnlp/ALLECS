#!/bin/bash

COMBINATION_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MEMT=$(dirname "$(dirname "$COMBINATION_PATH")")
MEMT_PORT_NUMBER=1994

export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MEMT/memt/install/boost_1_49_0/stage/lib"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MEMT/memt/install/icu/source/lib"

# test data here
$MEMT/memt/MEMT/Alignment/match.sh $COMBINATION_PATH/GECToR-Roberta.txt $COMBINATION_PATH/GECToR-XLNet.txt > matched
$MEMT/memt/MEMT/scripts/simple_decode.rb $MEMT_PORT_NUMBER decoder_config matched
