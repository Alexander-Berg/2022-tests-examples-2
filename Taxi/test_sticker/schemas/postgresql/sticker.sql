\set role testsuite
\ir ../../../sticker/storage/postgresql/migrations/00_initial.sql
\ir ../../../sticker/storage/postgresql/migrations/01_expire_indexes.sql
\ir ../../../sticker/storage/postgresql/migrations/02_indexes_for_monrun.sql
\ir ../../../sticker/storage/postgresql/migrations/03_add_body_hash_index.sql
\ir ../../../sticker/storage/postgresql/migrations/04_add_reason_field.sql
\ir ../../../sticker/storage/postgresql/migrations/05_attachments_table.sql
\ir ../../../sticker/storage/postgresql/migrations/06_per_row_lock.sql
\ir ../../../sticker/storage/postgresql/migrations/07_send_after.sql
\ir ../../../sticker/storage/postgresql/migrations/08_send_after_index.sql
\ir ../../../sticker/storage/postgresql/migrations/09_add_email_column.sql
\ir ../../../sticker/storage/postgresql/migrations/10_drop_extra.sql
\ir ../../../sticker/storage/postgresql/migrations/11_add_raw_recipient_type.sql
\ir ../../../sticker/storage/postgresql/migrations/12_add_other_recipients_field.sql
\ir ../../../sticker/storage/postgresql/migrations/13_add_via_sender_field.sql
\ir ../../../sticker/storage/postgresql/migrations/14_add_sender_account_field.sql
\ir ../../../sticker/storage/postgresql/migrations/15_add_tvm_name.sql
