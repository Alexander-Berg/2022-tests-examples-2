INSERT INTO supportai.states (project_id, chat_id, state)
VALUES
(
 'sample_project',
 '1', $$
 {
    "feature_layers":[
        {"iteration_number": {"key": "iteration_number", "value": 2, "status": "defined", "type": "int", "can_be_found_without_question": false}},
        {"iteration_number": {"key": "iteration_number", "value": 1, "status": "defined", "type": "int", "can_be_found_without_question": false}}
    ]
  }
$$)
