CREATE TABLE IF NOT EXISTS "{{ name | i }}" (
    "id"    SERIAL NOT NULL PRIMARY KEY,
    "name"  TEXT NOT NULL
)
