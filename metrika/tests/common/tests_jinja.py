import metrika.admin.python.bishop.frontend.bishop.jinja as bp_jinja


TEMPLATE_TEXT = '''{% if variable_a == "1" %}
    {{ variable_b }}
    {% include "include_a" %}
{% else %}
    {{ variable_c }}
    {% include "include_b" %}
{% endif %}

{% for key in variable_d %}
    {{ key }} -> {{ variable_e }}
{% endfor %}

{% do variable_f.append('c') %}

{% set value = variable_g %}

{{ variable_j|default("j") }}
{{ variable_k|default(variable_l|default(variable_m)) }}
{% set include_d = "include_d" %}

{% include "include_c" %}
{% include include_d %}
'''


def test_get_template_undeclared():
    expected_variables = [
        'variable_a',
        'variable_b',
        'variable_c',
        'variable_d',
        'variable_e',
        'variable_f',
        'variable_g',
        'variable_j',
        'variable_k',
        'variable_l',
        'variable_m',
    ]
    variables = bp_jinja.get_template_undeclared(
        TEMPLATE_TEXT,
        load_templates_map=False,
    )
    assert sorted(variables) == expected_variables


def test_get_template_referenced():
    expected_includes = [
        'include_a',
        'include_b',
        'include_c',
        None,  # If dynamic inheritance or inclusion is used, None will be yielded. // jinja2 find_referenced_templates
    ]
    includes = bp_jinja.get_template_referenced(
        TEMPLATE_TEXT,
        load_templates_map=False,
    )
    assert includes == expected_includes
