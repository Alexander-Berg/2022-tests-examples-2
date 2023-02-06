INSERT INTO task_processor.providers (name, tvm_id, tvm_name, updated_at, hostname)
VALUES ('clown', 1, '', extract (epoch from now()), '');

INSERT INTO task_processor.cubes (name, provider_id, needed_parameters, optional_parameters, output_parameters, updated_at)
VALUES ('A', 1, '["in_param1"]'::jsonb, '[]'::jsonb, '["out_param1"]'::jsonb, extract (epoch from now()));
