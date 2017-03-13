#!/usr/bin/env bash
set -e

cd '/usr';
sudo mysqld_safe --user=root --datadir='/var/lib/mysql' &
cd -

