import asyncio
import json
import logging
import time
import traceback
from random import shuffle
from itertools import cycle
from concurrent.futures import TimeoutError as concurrent_TimeoutError
from typing import Optional, Union  # noqa

import aiohttp
import requests
import tenacity
import ssl
import certifi

base_logger = logging.getLogger(__name__)


class SplunkHECSender(object):
    """
    Class for sending data to SOC Splunk cluster via Http Event Collector.
    Token most be described on cluster side config (Contact SOC team).
    Main method (function) - send_data(data).
    Basic usage:
    1. object = SplunkHECSender("TOKEN")
    2. object.send_data(data_variable) # Data can be: dict or list of dicts.
    Retries class attributes (to use in decorators):
    * retries_count (default 5)
    * retries_min_delay (default 0.5)
    * retries_max_delay (default 2.0)
    * retries_timeout (default 10)
    """

    retries_count = 5
    retries_min_delay = 0.5
    retries_max_delay = 2.0
    retries_timeout = 10

    def __init__(self,
                 token,  # type: str
                 src_host=None,  # type: Optional[str]
                 index=None,  # type: Optional[str]
                 source=None,  # type: Optional[str]
                 sourcetype=None,  # type: Optional[str]
                 current_time_as_timestamp=False,  # type: bool
                 timestamp=None,  # type: Optional[str]
                 hec_host="hatch.yandex.net",  # type: str
                 hec_host_port=None,  # type: Optional[int]
                 hec_verify_ssl=True,  # type: bool
                 batch_size=100,  # type: int
                 threads=10,  # type: int
                 sourcetype_field_name=None,  # type: Optional[str]
                 source_field_name=None,  # type: Optional[str]
                 timestamp_field_name=None,  # type: Optional[str]
                 post_timeout=3,  # type: int
                 hec_hosts=None,  # type: Optional[set]
                 hec_hosts_switch_timeout=10  # type: int
                 ):
        # type: (...) -> None
        """
        Arguments can be divided into this logical categories:
        * Splunk HEC settings (token, src_host, hec_host, hec_verify_ssl)
        * Events main fields defaults (index, source, sourcetype, timestamp, current_time_as_timestamp,
            sourcetype_field_name, source_field_name, timestamp_field_name)
        * Events processings parameters (batch_size, threads, post_timeout, retries_count, retries_min_delay,
            retries_max_delay, retries_timeout)
        Default retries settings: 5 retries with delay 0.3s with total timeout for all retries 20s.
        .. note::
            You can provide all required default Splunk fields (time, index, source, sourcetype) values via
            "__meta" field in every single event. Values from meta field will have priority above described arguments.
        :param token: Splunk HEC token string (from inputs.conf)
        :type token: str
        :param src_host: Splunk HEC host (defaults to SOC Splunk cluster load balancer: hatch.yandex.net)
        :type src_host: str
        :param index: Splunk index field value. If provided, will be applied to ALL events if index not provided in
            event metadata (__meta field)
        :type index: str
        :param source: Splunk source field value. If provided, will be applied to ALL events if source not provided in
            event metadata (__meta field)
        :type source: str
        :param sourcetype: Splunk sourcetype field value. If provided, will be applied to ALL events if sourcetype
            not provided in event metadata (__meta field)
        :type sourcetype: str
        :param current_time_as_timestamp: Defaults to False. If True - ALL events time field will be set to processing
            time.
        :type current_time_as_timestamp: bool
        :param timestamp: Timestamp in unix epoch time format as string. Will be applied as default time value to ALL
            events;
        :type timestamp: str
        :param hec_host: Splunk HEC endpoint hostname
        :type hec_host: str
        :param hec_host_port: Splunk HEC endpoint target port. Default to 443
        :type hec_host_port: int
        :param hec_verify_ssl: SSL verification in HTTP requests. Defaults to True.
        :type hec_verify_ssl: bool
        :param batch_size: Max number of events to be processed in single POST request. Defaults to 100.
        :type batch_size: int
        :param threads: Number of threads which can be used, then processing data size has more events then described
            in batch_size. So the events count will be divided by batch_size number and processed in provided here
            number of threads. If number of divided parts is bigger then number of threads - then excess number of
            threads will sequentially, after first bunch of threads finishes it work.
        :type threads: int
        :param sourcetype_field_name: Splunk sourcetype field name value. If provided, value for sourcetype field will
            be extracted from each event using provided field name, if no event metadata (__meta field) provided.
        :type sourcetype_field_name: str
        :param source_field_name: Splunk source field name value. If provided, value for source field will
            be extracted from each event using provided field name, if no event metadata (__meta field) provided.
        :type source_field_name: str
        :param timestamp_field_name: Splunk time field name value. If provided, value for time field will
            be extracted from each event using provided field name, if no event metadata (__meta field) provided.
        :type timestamp_field_name: str
        :param post_timeout: Single post request timeout in seconds. Defaults to 3 seconds.
        :type post_timeout: int
        :param hec_hosts: For load balancing purposes.
            This argument has priority over hec_host and load balancing mode will be enabled if it is provided.
            Hosts list will be randomly shuffled at initialization.
            Basic round-robin will be used with timeout for hosts switching.
        :type hec_hosts: set
        :param hec_hosts_switch_timeout: Will only be respected if hec_hosts is used.
            Timeout in seconds, after which logs sending will be switched to the next host.
            Defaults to 10 seconds.
        :type hec_hosts_switch_timeout: int
        """

        # HEC attributes
        self._hec_host = hec_host
        self.hec_host_port = hec_host_port
        self.token = token
        auth_header = "Splunk {}".format(self.token)
        self.auth_header = {"Authorization": auth_header}
        self.batch_size = batch_size
        # Fields attributes
        self.src_host = src_host
        self.index = index
        self.source = source
        self.sourcetype = sourcetype
        self.threads = threads
        self.sourcetype_field_name = sourcetype_field_name
        self.source_field_name = source_field_name
        self.timestamp_field_name = timestamp_field_name
        self.post_timeout = post_timeout
        self.logger_extra = {"traceback_trace": json.dumps({})}
        self.current_time_as_timestamp = current_time_as_timestamp
        self.timestamp = timestamp

        self.hec_hosts = None

        if hec_hosts is not None:
            self.hec_hosts = list(hec_hosts)
            shuffle(self.hec_hosts)
            self.hec_hosts = cycle(self.hec_hosts)
            self._hec_host = next(self.hec_hosts)

        self.hec_hosts_switch_timeout = hec_hosts_switch_timeout

        self.connection_pool = aiohttp.TCPConnector(limit=self.threads)

        # Verify SSL
        self.hec_verify_ssl = hec_verify_ssl
        # Should be, even if verify ssl is disabled
        self.proto = "https"
        if not self.hec_verify_ssl:
            requests.packages.urllib3.disable_warnings()

        if isinstance(self.hec_host_port, int):
            self.request_url_base = f"{self.proto}://{{}}:{self.hec_host_port}/services/collector"
        else:
            self.request_url_base = f"{self.proto}://{{}}/services/collector"

        self.checkpoint_time = time.time()

    def __del__(self):
        self.connection_pool.close()

    @property
    def hec_timeout_reached(self):
        if time.time() - self.checkpoint_time > self.hec_hosts_switch_timeout:
            return True
        else:
            return False

    @property
    def hec_host(self):
        """
        Return current hec_host, based on operating modes.
        For single instance - return value from init argument.
        For load balancing - return next in cycle from hec_hosts if timeout reached.
        """

        if self.hec_hosts is not None and self.hec_timeout_reached:
            self.checkpoint_time = time.time()
            self._hec_host = next(self.hec_hosts)

        self.logger.debug("HEC host value: %s", self._hec_host)
        return self._hec_host

    @property
    def request_url(self):
        request_url = self.request_url_base.format(self.hec_host)
        self.logger.debug("HEC request url: %s", request_url)

        return request_url

    @property
    def logger(self):
        """
        Prepare logger property with extra fields for Qloud logging.
        :return: Logger instance with extra fields provided to match required format.
        :rtype: logging.Logger
        """
        logger = logging.LoggerAdapter(base_logger, self.logger_extra)
        return logger

    @tenacity.retry(retry=(tenacity.retry_if_exception_type(IOError) |
                           tenacity.retry_if_exception_type(asyncio.TimeoutError) |
                           tenacity.retry_if_exception_type(concurrent_TimeoutError) |
                           tenacity.retry_if_exception_type(aiohttp.client_exceptions.ServerDisconnectedError)),
                    wait=tenacity.wait_fixed(retries_min_delay) + tenacity.wait_random(min=retries_min_delay,
                                                                                       max=retries_max_delay),
                    stop=(tenacity.stop_after_attempt(retries_count) | tenacity.stop_after_delay(retries_timeout)))
    async def async_post_request(self, url, data, headers, verify, timeout, session):
        # type: (str, str, dict, bool, aiohttp.ClientTimeout, aiohttp.client.ClientSession) -> int
        """
        Method to send single POST request via aiohttp lib.
        :param url: Target url
        :type url: str
        :param data: Data to be send
        :type data: str
        :param headers: Headers for request
        :type headers: dict
        :param verify: SSL verify setting for request
        :type verify: bool
        :param timeout: POST request timeout value
        :type timeout: aiohttp.ClientTimeout
        :param session: Aiohttp Session with provided number of TCP connections
        :type session: aiohttp.client.ClientSession
        :return: Requests status code
        :rtype: int
        :raises IOError - returned status code in [503, 502. 413, 429]
        """

        if verify:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
        else:
            ssl_context = False

        async with session.post(url, data=data, headers=headers, ssl=ssl_context,
                                timeout=timeout) as response:
            if response.status in [503, 502, 413, 429]:
                self.logger.error("POST FAILED! Status code: %d; "
                                  "Response text: %s", response.status, await response.text())
                raise IOError
            else:
                return response.status

    async def async_post_request_batch(self, data):
        # type: (list) -> None
        """
        Method to process prepared batch of events in provided number of threads.
        :param data: Prepared events batch
        :type data: list
        :return: None
        :rtype: None
        """
        timeout = aiohttp.ClientTimeout(total=self.post_timeout)
        tasks = list()

        async with aiohttp.ClientSession(timeout=timeout,
                                         connector=self.connection_pool,
                                         connector_owner=False) as session:
            for part in data:
                post_batch_events_part = "\n".join(part)
                task = asyncio.ensure_future(self.async_post_request(url=self.request_url,
                                                                     data=post_batch_events_part,
                                                                     headers=self.auth_header,
                                                                     verify=self.hec_verify_ssl,
                                                                     timeout=timeout,
                                                                     session=session
                                                                     ))
                if len(tasks) < self.threads:
                    tasks.append(task)
                else:
                    request = asyncio.gather(*tasks)
                    tasks.clear()
                    await request

            if len(tasks) > 0:
                request = asyncio.gather(*tasks)
                await request

    @staticmethod
    def _get_current_time():
        """
        Method to get current time.
        :return:
        :rtype:
        """
        timestamp = str(time.time())
        return timestamp

    @staticmethod
    def _slice_list(array, size):
        # type: (list, int) -> list
        """
        Slice list into lists with provided size.
        :param array: List for slicing
        :type array: list
        :param size: Required size of list
        :type size: list
        :return: List of sliced lists with required size
        :rtype: list
        """
        for i in range(0, len(array), size):
            yield array[i:i + size]

    @tenacity.retry(retry=(tenacity.retry_if_exception_type(IOError) |
                           tenacity.retry_if_exception_type(asyncio.TimeoutError) |
                           tenacity.retry_if_exception_type(concurrent_TimeoutError) |
                           tenacity.retry_if_exception_type(aiohttp.client_exceptions.ServerDisconnectedError)),
                    wait=tenacity.wait_fixed(retries_min_delay) + tenacity.wait_random(min=retries_min_delay,
                                                                                       max=retries_max_delay),
                    stop=(tenacity.stop_after_attempt(retries_count) | tenacity.stop_after_delay(retries_timeout)))
    def send_post_request(self, prep_data):
        """
        Method to send single POST request via requests lib.
        :param prep_data:
        :type prep_data:
        :return: True if HEC successfully received data. False otherwise.
        :rtype: bool
        :raises: IOError - if failed to post data to splunk. Retries will be useed
        """
        post_request = requests.post(self.request_url, data=prep_data,
                                     headers=self.auth_header,
                                     verify=self.hec_verify_ssl,
                                     timeout=self.post_timeout)

        response_json = json.loads(str(post_request.text))
        response = post_request.text
        if "text" in response_json and post_request.status_code == 200:
            if response_json["text"] != "Success":
                self.logger.error("Request post failed, response: %s; "
                                  "Status code: %d", response, post_request.status_code)
                raise IOError
            else:
                return True

        return False

    def prepare_event_time_field(self, event):  # noqa: C901
        # type: (dict) -> Optional[str]
        """
        Method to prepare
        Provided time field value must be in unix epoch time as a string!
        Priority:
        1. __meta field in event
        2. self.timestamp_field_name if exist in event
        3. self.timestamp value - one for all events
        :param event: Current processing event, for which prepare timestamp
        :type event: dict
        :return: Timestring in unix epoch timeformat.
        :rtype: str
        """

        event_time = None

        if ("__meta" in event and isinstance(event["__meta"], dict) and "timestamp" in event["__meta"] and
                event["__meta"]["timestamp"] is not None):
            event_time = event["__meta"]["timestamp"]

        elif self.timestamp_field_name is not None:
            try:
                event_time = event[self.timestamp_field_name]
            except KeyError:
                tb_trace = traceback.format_exc()
                self.logger_extra["traceback_trace"] = tb_trace
                self.logger.error("Timestamp field %s not found in event!", self.timestamp_field_name)
                self.logger_extra["traceback_trace"] = json.dumps({})
        elif self.timestamp is not None:
            event_time = self.timestamp
        elif self.current_time_as_timestamp:
            event_time = self._get_current_time()

        if event_time is not None:
            try:
                float(event_time)
            except ValueError:
                event_time = None
                self.logger.info("Provided timestamp not in epoch format! Returning None instead. "
                                 "Provided time: %s, provided type: %s", event_time, type(event_time))

        return event_time

    def prepare_event_field_value_by_name(self, event, field):
        # type: (dict, str) -> Optional[str]
        """
        Method to prepare provided field value.
        Priority:
        1. __meta field in event
        2. self.<field>_field_name if exist in event
        3. self.<field> value - one for all events
        :param event: Current processing event
        :type event: dict
        :param field: Splunk field name which value to prepare for curent event
        :type field: str
        :return: Required field value
        :rtype: str
        """
        result = None
        field_name = "_".join([field, "field_name"])

        if ("__meta" in event and isinstance(event["__meta"], dict) and field in event["__meta"] and
                event["__meta"][field] is not None):
            result = event["__meta"][field]

        elif hasattr(self, field) and getattr(self, field) is not None:
            result = getattr(self, field)

        elif hasattr(self, field_name) and getattr(self, field_name) is not None:
            try:
                result = event[getattr(self, field_name)]
            except KeyError:
                self.logger.error("%s field not found in event!", field_name)

        return result

    def send_data(self, data, loop):  # noqa: C901
        # type: (Union[list, dict]) -> bool
        """
        Main method.
        Provide data which needs to be send to Splunk via HEC.
        Use __meta field for custom source, sourcetype, index definition for single event.
        :param data:
        :type data:
        :return: Always returns True. If failed to send data - then exception will be raised.
        :rtype: bool
        :raises: TypeError - if data not list of dicts or dict.
        """
        # Prepare metadata
        post_event = dict()
        post_batch_events = list()

        if self.src_host is not None:
            post_event.update({"host": self.src_host})

        # If input is list of dicts, then batch events in one request, else send single events
        if isinstance(data, list):
            # Prepare string
            for event in data:
                if not isinstance(event, dict):
                    raise TypeError("Events must be 'dict' type!")

                event_time = self.prepare_event_time_field(event)
                sourcetype = self.prepare_event_field_value_by_name(event, "sourcetype")
                source = self.prepare_event_field_value_by_name(event, "source")
                index = self.prepare_event_field_value_by_name(event, "index")

                if source is not None:
                    post_event.update({"source": source})

                if sourcetype is not None:
                    post_event.update({"sourcetype": sourcetype})

                if index is not None:
                    post_event.update({"index": index})

                if event_time is not None:
                    post_event.update({"time": event_time})

                event.pop("__meta", None)

                if "__message" in event:
                    processing_event = event["__message"]
                else:
                    processing_event = event

                res = {"event": processing_event}
                res.update(post_event)
                res = json.dumps(res)
                post_batch_events.append(res)

            if len(post_batch_events) > self.batch_size:
                self.logger.info("Count of events %d > batch size %d, "
                                 "splitting to multiple requests", len(post_batch_events), self.batch_size)

                post_batch_events_sliced = list(self._slice_list(post_batch_events, self.batch_size))



                asyncio.create_task(self.async_post_request_batch(post_batch_events_sliced))


            else:
                self.logger.info("Count of events < batch size, sending in single post request")
                post_batch_events = "\n".join(post_batch_events)
                request = self.send_post_request(post_batch_events)
                self.logger.debug("Single POST request status (True if success): %s", request)

        elif isinstance(data, dict):
            event_time = self.prepare_event_time_field(data)
            if event_time is not None:
                post_event.update({"time": event_time})

            post_event.update({"event": data})

            post_event = json.dumps(post_event)
            self.logger.debug("Single event passed as dict, sending post request ...")
            request = self.send_post_request(post_event)
            self.logger.debug("Single POST request status (True if success): %s", request)

        else:
            raise TypeError("Wrong data type provided!")

        return True