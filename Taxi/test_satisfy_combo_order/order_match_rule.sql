INSERT INTO combo_contractors.order_match_rule (
  name, expression, compiled_expression, updated
)
VALUES
(
  'always_true',
  '1.0',
  '{"rpn_tokens": [{"number": 1.0}], "parameters": {}, "parameter_names": []}',
  '2001-9-9 01:46:39'
),
(
  'regular_combo',
  'cb1_dist-b2b1_dist>x_dist && cb1_time-b2b1_time>x_time &&
   (cb1_dist-b2b1_dist)/cb1_dist>y_dist &&
   (cb1_time-b2b1_time)/cb1_time>y_time && ca2_dist<z_dist &&
   ca2_time<z_time',
  '{
     "parameter_names": [
       "b2b1_dist",
       "b2b1_time",
       "ca2_dist",
       "ca2_time",
       "cb1_dist",
       "cb1_time",
       "x_dist",
       "x_time",
       "y_dist",
       "y_time",
       "z_dist",
       "z_time"
     ],
     "parameters": {
       "x_dist": 100500.0,
       "x_time": 500.0,
       "y_dist": 0.5,
       "y_time": 0.5,
       "z_dist": 1000.0,
       "z_time": 100
     },
     "rpn_tokens": [
       {"parameter": "cb1_dist"},
       {"parameter": "b2b1_dist"},
       {"op_code": "sub"},
       {"parameter": "x_dist"},
       {"op_code": "gt"},
       {"parameter": "cb1_time"},
       {"parameter": "b2b1_time"},
       {"op_code": "sub"},
       {"parameter": "x_time"},
       {"op_code": "gt"},
       {"op_code": "logic_and"},
       {"parameter": "cb1_dist"},
       {"parameter": "b2b1_dist"},
       {"op_code": "sub"},
       {"parameter": "cb1_dist"},
       {"op_code": "div"},
       {"parameter": "y_dist"},
       {"op_code": "gt"},
       {"op_code": "logic_and"},
       {"parameter": "cb1_time"},
       {"parameter": "b2b1_time"},
       {"op_code": "sub"},
       {"parameter": "cb1_time"},
       {"op_code": "div"},
       {"parameter": "y_time"},
       {"op_code": "gt"},
       {"op_code": "logic_and"},
       {"parameter": "ca2_dist"},
       {"parameter": "z_dist"},
       {"op_code": "lt"},
       {"op_code": "logic_and"},
       {"parameter": "ca2_time"},
       {"parameter": "z_time"},
       {"op_code": "lt"},
       {"op_code": "logic_and"}
     ]
   }',
  '2001-9-9 01:46:39'
),
(
  'promised_time_check',
  'promised_time_left<time_bound',
  '{
    "parameter_names": [
      "promised_time_left"
    ],
    "parameters": {
      "time_bound": 2000
    },
    "rpn_tokens": [
      {"parameter": "promised_time_left"},
      {"parameter": "time_bound"},
      {"op_code": "lt"}
    ]
  }',
  '2001-9-9 01:46:39'
)
