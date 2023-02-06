/* V1 */
INSERT INTO scripts.js_scripts
(id, bonus_name, revision, type, content)
VALUES
(1, 'bonus_1', 0, 'calculate', 'return 1'),
(2, 'bonus_1', 1, 'calculate', 'return 2'),
(3, 'bonus_1', 2, 'calculate', 'return 3'),
(4, 'bonus_2', 0, 'calculate', 'return 10'),
(5, 'bonus_2', 1, 'calculate', 'will not compile'),
(6, 'script_1', 0, 'postprocess_results', 'return {"foo": "bar"}');

INSERT INTO scripts.active_scripts
(id, bonus_name, type, script_id)
VALUES
(1, 'bonus_1', 'calculate', 2);
