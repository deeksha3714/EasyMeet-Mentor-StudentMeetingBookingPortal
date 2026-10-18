#!/bin/bash
set -e

DB_NAME="easymeet"

read -s -p "New user name: " DB_USER
echo
read -s -p "New user password: " USER_PASS
echo

sudo mysql <<SQL
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost'
IDENTIFIED BY '$USER_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
SQL

sudo mysql -u "$DB_USER" -p"$USER_PASS" "$DB_NAME" < schema.sql

echo "Database setup completed successfully!"

