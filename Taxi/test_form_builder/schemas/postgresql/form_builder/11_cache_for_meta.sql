CREATE TABLE caches.metas (
    form_code TEXT REFERENCES form_builder.forms(code) ON DELETE CASCADE NOT NULL,
    submit_id TEXT NOT NULL,
    data JSONB NOT NULL
);

CREATE UNIQUE INDEX uniq_meta_ident_idx
    ON caches.metas(form_code, submit_id);
