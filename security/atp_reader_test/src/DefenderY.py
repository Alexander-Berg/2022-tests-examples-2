import logging
import yaml
import json
import asyncio
import signal
from aiohttp import ClientSession
from hec_sender import SplunkHECSender

from datetime import datetime, timedelta


def division(a):
    return a
    
class DefenderY:
    def __init__(self, config_path):
        self.config = self.__load_config(config_path)

        self.loop = asyncio.get_event_loop()
        self.headers = None

        # обьекты Hec Sender
        self.alerts_hec_connector = SplunkHECSender(self.config['hec_token'],
                                                    index=self.config['defender_alerts_index'],
                                                    sourcetype=self.config['defender_alerts_sourcetype'],
                                                    hec_verify_ssl=False)

        self.hosts_hec_connector = SplunkHECSender(self.config['hec_token'],
                                                   index=self.config['defender_hosts_index'],
                                                   sourcetype=self.config['defender_hosts_sourcetype'],
                                                   hec_verify_ssl=False)
        self.cve_hec_connector = SplunkHECSender(self.config['hec_token'],
                                                   index=self.config['defender_cve_index'],
                                                   sourcetype=self.config['defender_cve_sourcetype'],
                                                   hec_verify_ssl=False)

    def run(self):
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            self.loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(self.shutdown(s, self.loop)))

        try:
            self.loop.create_task(self.get_aadToken())
            self.loop.create_task(self.get_alerts())
            self.loop.create_task(self.get_hosts())
            self.loop.create_task(self.get_cve())
            self.loop.run_forever()
        finally:
            logging.info("Successfully shutdown DefenderY")
            self.loop.close()

    ############################
    #  Вспомогательные функции #
    ############################

    @staticmethod
    async def shutdown(signal, loop):
        logging.info(f"Received exit signal {signal.name}...")
        logging.info("Nacking tasks")
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]

        [task.cancel() for task in tasks]

        logging.info(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        logging.info(f"Flushing metrics")
        loop.stop()

    @staticmethod
    def __load_config(config_path: str):
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
        logging.info("DefenderY loaded config")
        return config

    # Update the AAD token
    async def get_aadToken(self):
        while True:
            url = f"https://login.windows.net/{self.config['defender']['tenantId']}/oauth2/token"
            resourceAppIdUri = 'https://api.securitycenter.windows.com'
            body = {
                'resource': resourceAppIdUri,
                'client_id': self.config['defender']['appId'],
                'client_secret': self.config['defender']['appSecret'],
                'grant_type': 'client_credentials'
            }
            try:
                async with ClientSession() as session:
                    async with session.get(url, data=body) as response:
                        if response.status == 200:
                            jsonResponse = json.loads(await response.text())
                            aadToken = jsonResponse["access_token"]
                            logging.info("Got aadToken")
                        else:
                            logging.error("Cant get aadToken")
            except Exception as ex:
                logging.error(f"Cant get aadToken : {str(ex)}")

            if aadToken:

                headers = {
                    'Authorization': "Bearer " + aadToken
                }
                self.headers = headers
                await asyncio.sleep(500)

    async def get_alerts(self):
        '''
        Получение Алертов из API Defender и отправка ее в Splunk
        :return:
        '''
        while True:
            logging.info("getting new alerts")
            filterTime = datetime.utcnow() - timedelta(
                minutes=self.config['alert_time_interval_min'])
            # If you want to include alerts from longer then an hour, change here (days, weeks)
            filterTime = filterTime.strftime("%Y-%m-%dT%H:%M:%SZ")
            url = f"https://api.securitycenter.windows.com/api/alerts?$filter=alertCreationTime+ge+{filterTime}+or+lastUpdateTime+ge+{filterTime}+{self.config['alert_filter']}"
            logging.info(f"request alert url: {url}")
            try:
                async with ClientSession(headers=self.headers) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            jsonResponse = json.loads(await response.text())
                            if len(jsonResponse['value']) > 0:
                                self.alerts_hec_connector.send_data(jsonResponse['value'], self.loop)
                            logging.info(f"Got alerts {len(jsonResponse['value'])}")
                            await asyncio.sleep(self.config['defender']['alert_delay'])
                        else:
                            logging.error(f"Cant get alerts. Response code {response.status}")
                            await asyncio.sleep(7)
            except Exception as ex:
                logging.error(f"Cant get alerts : {str(ex)}")

    async def get_hosts(self):
        '''
        Получение списка хостов из API Defender и отправка ее в Splunk
        :return:
        '''
        while True:
            logging.info("getting hosts info")
            url = f"https://api.securitycenter.microsoft.com/api/machines"
            try:
                async with ClientSession(headers=self.headers) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            jsonResponse = json.loads(await response.text())
                            if len(jsonResponse['value']) > 0:
                                self.hosts_hec_connector.send_data(jsonResponse['value'], self.loop)
                            logging.info(f"Got machines {len(jsonResponse['value'])}")
                            await asyncio.sleep(self.config['defender']['host_delay'])
                        else:
                            logging.error(f"Cant get machines. Response code {response.status}")
                            await asyncio.sleep(7)
            except Exception as ex:
                logging.error(f"Cant get machines : {str(ex)}")



    async def get_cve(self):
         while True:
            logging.info("getting cve info")
            get_servers_url = f"https://api.securitycenter.microsoft.com/api/machines?$filter=startswith(osPlatform,'WindowsServer')"
            try:
                async with ClientSession(headers=self.headers) as session:
                    machineIds = []
                    async with session.get(get_servers_url) as response:
                        if response.status == 200:
                            jsonResponse = json.loads(await response.text())
                            if len(jsonResponse['value']) > 0:

                                #self.hosts_hec_connector.send_data(jsonResponse['value'], self.loop)
                                for i in jsonResponse['value']:
                                    a = {"id": i.get("id"), "computerDnsName": i.get("computerDnsName")}
                                    machineIds.append(a)
                            logging.info(f"Got cve {len(jsonResponse['value'])}")
                        else:
                            logging.error(f"Cant get cve. Response code {response.status}")
                            await asyncio.sleep(7)

                    for machineId in machineIds:
                        id = machineId["id"]
                        async with session.get(f"https://api-eu.securitycenter.windows.com/api/machines/{id}/vulnerabilities") as response_2:
                            if response_2.status == 200:
                                servers_cve = json.loads(await response_2.text())
                                for cve in servers_cve['value']:
                                    cve["id_computer"] = id
                                    cve["computerDnsName"] = machineId["computerDnsName"]
                                self.cve_hec_connector.send_data(servers_cve['value'], self.loop)
                            else:
                                logging.error(f"Cant get cve for devices. Response code {response_2.status}")
                                await asyncio.sleep(7)
                    await asyncio.sleep(self.config['defender']['cve_delay'])

            except Exception as ex:
                logging.error(f"Cant get cve: {str(ex)}")
