{{ YENV_NAME }}
{{ YENV_TYPE }}

{% set secret_data = data | from_json %}

LOGIN = {{ secret_data.login }}
PASSWORD = {{ secret_data.password }}

TOKEN_1 = {{ secret_data | json_query('tokens[0]') }}
TOKEN_2 = {{ secret_data.tokens.1 }}
