INSERT INTO combo_contractors.order_match_rule (
  name, expression, compiled_expression, updated
)
VALUES
(
  'score0',
  '1 -
    (transporting_time_0 +
     transporting_time_1 -
     base_transporting_time_0 -
     base_transporting_time_1
    ) /
    (transporting_time_0 +
     transporting_time_1)',
  '{
    "rpn_tokens":[
      {
        "number":1.0
      },
      {
        "parameter":"transporting_time_0"
      },
      {
        "parameter":"transporting_time_1"
      },
      {
        "op_code":"add"
      },
      {
        "parameter":"base_transporting_time_0"
      },
      {
        "op_code":"sub"
      },
      {
        "parameter":"base_transporting_time_1"
      },
      {
        "op_code":"sub"
      },
      {
        "parameter":"transporting_time_0"
      },
      {
        "parameter":"transporting_time_1"
      },
      {
        "op_code":"add"
      },
      {
        "op_code":"div"
      },
      {
        "op_code":"sub"
      }
    ],
    "parameters":null,
    "parameter_names":[
      "base_transporting_time_1",
      "base_transporting_time_0",
      "transporting_time_1",
      "transporting_time_0"
    ]
  }',
  '2001-9-9 01:46:39'
),
(
  'filter0',
  '  past_time_0 + left_time_0 - base_transporting_time_0 > time_delta
   || transporting_time_1 - base_transporting_time_1 > time_delta',
  '{
    "rpn_tokens":[
      {
        "parameter":"past_time_0"
      },
      {
        "parameter":"left_time_0"
      },
      {
        "op_code":"add"
      },
      {
        "parameter":"base_transporting_time_0"
      },
      {
        "op_code":"sub"
      },
      {
        "parameter":"time_delta"
      },
      {
        "op_code":"gt"
      },
      {
        "parameter":"transporting_time_1"
      },
      {
        "parameter":"base_transporting_time_1"
      },
      {
        "op_code":"sub"
      },
      {
        "parameter":"time_delta"
      },
      {
        "op_code":"gt"
      },
      {
        "op_code":"logic_or"
      }
    ],
    "parameters":null,
    "parameter_names":[
      "base_transporting_time_1",
      "transporting_time_1",
      "time_delta",
      "base_transporting_time_0",
      "left_time_0",
      "past_time_0"
    ]
  }',
  '2001-9-9 01:46:39'
);
