"""Database-level guarantees Django cannot express (docs/design/01-domain-model.md §16).

- pg_trgm for fuzzy search (on RDS also created by infra/sql/bootstrap.sql, register R-55).
- core_forbid_update(): reusable trigger function for append-only tables. AuditLog uses it now;
  the credit ledger reuses it in M4.
- Outbox payloads must be JSON objects.
"""

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations

FORBID_UPDATE_FN = """
CREATE OR REPLACE FUNCTION core_forbid_update() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'table % is append-only: % is not allowed', TG_TABLE_NAME, TG_OP
        USING ERRCODE = 'insufficient_privilege';
END;
$$;
"""

AUDITLOG_TRIGGER = """
CREATE TRIGGER trg_auditlog_append_only
    BEFORE UPDATE ON core_auditlog
    FOR EACH ROW EXECUTE FUNCTION core_forbid_update();
"""


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]

    operations = [
        TrigramExtension(),
        migrations.RunSQL(FORBID_UPDATE_FN, "DROP FUNCTION IF EXISTS core_forbid_update();"),
        migrations.RunSQL(
            AUDITLOG_TRIGGER, "DROP TRIGGER IF EXISTS trg_auditlog_append_only ON core_auditlog;"
        ),
        migrations.RunSQL(
            "ALTER TABLE core_outboxmessage ADD CONSTRAINT ck_outbox_payload_object "
            "CHECK (jsonb_typeof(payload) = 'object');",
            "ALTER TABLE core_outboxmessage DROP CONSTRAINT ck_outbox_payload_object;",
        ),
    ]
