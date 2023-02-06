from jinja2 import Environment, BaseLoader
from sandbox import sdk2

TEMPLATE = """
<table border="1" bordercolor="green" cellpadding="10" >
<tbody>
{% for test in tests %}
  <tr>
    <td>{{ test['name'] }}</td>
    <td>{{ test['status'] }}</td>
    {% if test['link'] %}
      <td><a href={{ test['link'] }}>{{ test['link'] }}</a></td>
    {% else %}
      <td>no link</td>
    {% endif %}
  </tr>
{% endfor %}
<tbody>
<table>
"""


class ReportMixin:
    @sdk2.header(title="Tests")
    def report(self):
        template = Environment(loader=BaseLoader).from_string(TEMPLATE)
        return template.render({
            "tests": self.Context.tests,
        })
