SELECT test_input, test_output, test_name 
FROM scripts.tests 
WHERE script_id = $1;
