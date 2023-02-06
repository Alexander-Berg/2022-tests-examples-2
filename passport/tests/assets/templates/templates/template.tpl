{{ YENV_NAME }}
{{ YENV_TYPE }}

{% for k, v in secret1|dictsort %}
    {{ k }} -> {{ v }}
{% endfor %}

DATABASE_LOGIN = {{ DB_LOGIN }}
DATABASE_PASSOWRD = {{ DB_PASSWORD }}

GLOBAL_VAR = {{ GLOBAL_VAR }}
LOCAL_VAR_1 = {{ LOCAL_VAR_1 }}
localVar2 = {{ localVar2 }}

local_password = {{ password }}
