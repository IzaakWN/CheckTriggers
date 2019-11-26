#! /bin/bash

sed -i 's/\x1B\[[0-9;]\+[A-Za-z]//g' $1

