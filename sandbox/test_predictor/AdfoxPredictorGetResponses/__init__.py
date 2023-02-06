import requests
import logging
import json
from sandbox import sdk2
from sandbox.projects.adfox.test_predictor.AdfoxPredictorRunTask import AdfoxPredictorRunTask


class Forecast:
    campaign_id = None
    current = None
    limit = None
    predicted = None

    def __init__(self, campaign_id, current, limit, predicted):
        self.campaign_id = campaign_id
        self.current = current
        self.limit = limit
        self.predicted = predicted

    def __repr__(self):
        return \
"""
campaign_id = {campaign_id}
current     = {current}
limit       = {limit}
predicted   = {predicted}
""".format(
    campaign_id=self.campaign_id,
    current=self.current,
    limit=self.limit,
    predicted=self.predicted,
)


class PredictorRequester:
    def __init__(self, network_ipv6, json_body_template, start_time):
        self.json_body_template = json_body_template
        self.start_time = start_time
        self.network_ipv6 = network_ipv6

    def request(self, owner_id, n_days):
        json_body = self.json_body_template.format(owner_id=owner_id, start_time=self.start_time)
        header = {
            'X-owner-id': str(owner_id),
            'X-ndays': str(n_days),
            'Content-Type': 'application/json',
            'x-forced-start-time': str(self.start_time),
        }
        url = "http://[" + self.network_ipv6 + "]:4445/predict"

        predictor_response = requests.post(
            url,
            data=json_body,
            headers=header
        )

        if predictor_response.status_code == 200:
            return self.return_200(predictor_response)

        return self.return_error(predictor_response, owner_id, n_days)

    def return_200(self, prediction_response):
        data = json.loads(prediction_response.text)
        result = list()

        for forecast_data in data['forecast']:
            forecast = Forecast(
                campaign_id=forecast_data['id'],
                current=forecast_data['imps'],
                limit=forecast_data['lim'],
                predicted=forecast_data['count']
            )

            result.append(forecast)

        return result

    def return_error(self, predictor_response, owner_id, n_days):
        logging.info(
            "Problems with prediction for {owner_id}, {days} days\ncode: {code}\nreason: {reason}".format(
                owner_id=owner_id,
                days=n_days,
                code=predictor_response.status_code,
                reason=predictor_response.reason
            )
        )


class AdfoxPredictorGetResponses(sdk2.Task):

    class Parameters(AdfoxPredictorRunTask.Parameters):
        path_to_samples = sdk2.parameters.String("Path to yt samples (filtered by owners)", required=True)
        owner_ids = sdk2.parameters.List("Top owner ids with unchanged campaigns", value_type=sdk2.parameters.Integer, required=True)
        predictor_json_body_template = sdk2.parameters.String("Template of json body", multiline=True, required=True)
        start_time = sdk2.parameters.Integer("Test start time", required=True)
        n_days = sdk2.parameters.Integer("Forecast for N days", required=True)

    def on_execute(self):
        with self.memoize_stage.run_predictor:
            self.run_predictor()

        with self.memoize_stage.collect_responses:
            ipv6 = self.predictor_run_task.Parameters.network_ipv6
            forecasts = self.collect_responses(ipv6)
            logging.info(forecasts)

    def run_predictor(self):
        logging.info(dict(self.Parameters))
        self.predictor_run_task = AdfoxPredictorRunTask(
            self,
            description="Child of {}".format(self.id),
            owner=self.owner,
            **dict(self.Parameters)
        )

        self.predictor_run_task.enqueue()

        raise sdk2.WaitOutput({self.predictor_run_task.id: "network_ipv6"}, wait_all=True, timeout=3600)

    def collect_responses(self, ipv6):
        requester = PredictorRequester(ipv6, self.Parameters.predictor_json_body_template, self.start_time)
        forecasts = dict()

        for owner_id in self.Parameters.owner_ids:
            forecasts[owner_id] = requester.request(owner_id, self.n_days)

        return forecasts
