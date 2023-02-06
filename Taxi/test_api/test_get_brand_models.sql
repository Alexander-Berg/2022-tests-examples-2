insert into cars_catalog.brand_models
(
    raw_brand,
    raw_model,
    normalized_mark_code,
    normalized_model_code,
    corrected_model
)
values
    ('Toyota', 'Corolla', 'TOYOTA', 'COROLLA', 'Toyota Corolla'),
    ('Toyota', null::text, null::text, null::text, null::text),
    ('Toyota', 'Camry', 'TOYOTA', 'CAMRY', 'Toyota Camry');
