INSERT INTO combo_contractors.order_match_rule (
  name, expression, compiled_expression, updated
)
VALUES
(
  'filter0',
  'transporting_time_0 > min_transporting_time && left_time_0 > min_left_time',
  '{
   "rpn_tokens":[
      {
         "parameter":"transporting_time_0"
      },
      {
         "parameter":"min_transporting_time"
      },
      {
         "op_code":"gt"
      },
      {
         "parameter":"left_time_0"
      },
      {
         "parameter":"min_left_time"
      },
      {
         "op_code":"gt"
      },
      {
         "op_code":"logic_and"
      }
   ],
   "parameters":null,
   "parameter_names":[
      "min_left_time",
      "left_time_0",
      "min_transporting_time",
      "transporting_time_0"
   ]
  }',
  '2001-9-9 01:46:39'
)
