-- RDS bootstrap, run once per database by the platform team (docs/architecture/04 §7.4, register R-55).
-- Extensions need rds_superuser on RDS, so the app's migration role cannot create them.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Guard rails for every application session (domain model §16, register R-54).
ALTER DATABASE CURRENT SET idle_in_transaction_session_timeout = '10s';
ALTER DATABASE CURRENT SET lock_timeout = '5s';
ALTER DATABASE CURRENT SET statement_timeout = '30s';

-- Roles (migrator, app, readonly, retention purge) and default privileges are added with the
-- Terraform dev environment.
