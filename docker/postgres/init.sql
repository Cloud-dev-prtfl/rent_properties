-- Local only. On RDS, extensions are created by infra/sql/bootstrap.sql (register R-55).
-- template1 gets them too, so pytest's test databases inherit them.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
\connect template1
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
