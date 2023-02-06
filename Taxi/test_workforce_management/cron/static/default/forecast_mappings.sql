INSERT INTO callcenter_operators.forecast_mapping (
    skill
    , mapping
)
VALUES
    ('russia', '{"line": "disp_ar"}'::JSONB)
    , ('russia', '{"line": "disp_ru"}'::JSONB)
    , ('nerussia', '{"line": "disp"}'::JSONB)
