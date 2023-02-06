# -*- coding: utf-8 -*-
import json
import sandbox.sdk2 as sdk2
from sandbox.projects.ydo import ydo_releasers


def save_json_data(self, resource_class, data, description, filename):
    with open(filename, 'w') as fout:
        fout.write(json.dumps(data, fout, ensure_ascii=False))

    resource = resource_class(
        self, description, filename
    )

    sdk2.ResourceData(resource).ready()
    return resource.id


class YdoSearchproxyTestWizardResponses(sdk2.Resource):
    releasers = ydo_releasers


class YdoSearchproxyTestPortalResponses(sdk2.Resource):
    releasers = ydo_releasers


class YappyBetaNameToUrlPrefix(sdk2.Task):
    class Parameters(sdk2.Parameters):
        beta_name = sdk2.parameters.String('beta name')
        template = sdk2.parameters.String(
            'template',
            default_value='{beta_name}.hamster'
        )
        with sdk2.parameters.Output:
            url_prefix = sdk2.parameters.String('url_prefix')

    def on_execute(self):
        self.Parameters.url_prefix = self.Parameters.template.format(
            beta_name=self.Parameters.beta_name
        )
