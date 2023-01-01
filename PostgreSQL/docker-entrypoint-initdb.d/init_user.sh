#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$PGUSER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER App;
	CREATE DATABASE stock_market;
	GRANT ALL PRIVILEGES ON stock_market docker TO App;
EOSQL
