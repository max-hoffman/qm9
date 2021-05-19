#!/bin/bash

set -eoux pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: `populate_db.sh <path>`"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null && pwd )"
BASE_DIR=$SCRIPT_DIR/..
DB=$BASE_DIR/$1
TMP=$BASE_DIR/tmp

labels=$TMP/labels.csv
features=$TMP/features.csv

rm -rf $TMP && mkdir -p $TMP

cd $BASE_DIR
poetry run python3 download.py $features $labels

if [ ! -d $DB ]; then
    mkdir -p $DB
    cd $DB
    dolt init
    dolt sql -q "create table qm9_features (id text primary key, atom_num int, elements json, coords json)"
    dolt table import --pk id --update-table qm9_features $features

    dolt sql -q "create table qm9_labels (A float, B float, C float, mu float, alpha float, homo float, lumo float, gap float, r2 float, zpve float, U0 float, U float, H float, G float, Cv float, id text primary key)"
    dolt table import --pk id --update-table qm9_labels $labels
fi
