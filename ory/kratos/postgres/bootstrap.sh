#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER kratos WITH PASSWORD 'kratos';
	CREATE DATABASE kratos;
	GRANT ALL PRIVILEGES ON DATABASE kratos TO kratos;
EOSQL
