INSERT INTO combo_contractors.order_match_rule (
  name, expression, compiled_expression, updated
)
VALUES
(
  'name0',
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
       "x_dist": 0.0,
       "x_time": 0.0,
       "y_dist": 0.0,
       "y_time": 0.0,
       "z_dist": 0.0,
       "z_time": 0.0
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
)
