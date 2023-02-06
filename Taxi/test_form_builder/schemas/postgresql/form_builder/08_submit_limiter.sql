CREATE TABLE form_builder.submit_limits (
    id SERIAL PRIMARY KEY,
    form_code TEXT REFERENCES form_builder.forms(code) ON DELETE CASCADE,
    field_code TEXT,
    max_count INTEGER,

    UNIQUE (form_code)
);

CREATE TABLE form_builder.limits (
    limiter INTEGER REFERENCES form_builder.submit_limits(id) ON DELETE CASCADE,
    value TEXT NOT NULL,
    current_count INTEGER NOT NULL DEFAULT 1,

    UNIQUE (limiter, value)
);
