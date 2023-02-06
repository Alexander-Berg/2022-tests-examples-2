from __future__ import unicode_literals, absolute_import, division, print_function

import logging
import requests

from sandbox import sdk2
from sandbox.sandboxsdk import environments


class GetTestflightVersions(sdk2.Task):

    class Parameters(sdk2.Task.Parameters):
        client_id = sdk2.parameters.String("Client id", default="", multiline=False)
        with sdk2.parameters.Output():
            versions_list = sdk2.parameters.String("List of versions in TestFlight")

    class Requirements(sdk2.Task.Requirements):
        environments = [
            environments.PipEnvironment('tvmauth', version='3.4.3'),
        ]

    def on_execute(self):
        from tvmauth import TvmClient, TvmApiClientSettings

        logging.info("Client id is `%s`", self.Parameters.client_id)

        secret = sdk2.yav.Secret('sec-01g7rdn3pe4qasayr719x2ypfp')
        client_secret = secret.data()['client_secret']

        tvm_settings = TvmApiClientSettings(
            self_tvm_id=2036070,
            self_secret=client_secret,
            enable_service_ticket_checking=False,
            dsts={'mb': 2001267}
        )

        tvm_client = TvmClient(tvm_settings)
        ticket = tvm_client.get_service_ticket_for('mb')

        client_id = self.Parameters.client_id
        url = "https://api.mediabilling.yandex.net/property/appstore-moderation-builds/get?clientId=%s" % client_id
        response = requests.get(url=url, headers={'X-Ya-Service-Ticket': ticket}).content

        self.Parameters.versions_list = response
