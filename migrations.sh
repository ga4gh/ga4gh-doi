#!/bin/bash

if [[ "$1" == "apply" ]]; then
    yoyo apply -b --database $DB_URL migrations --no-cache
elif [[ "$1" == "rollback" ]]; then 
    yoyo rollback -b --database $DB_URL -v migrations --no-cache -r $2
else 
    echo "invalid command"
fi