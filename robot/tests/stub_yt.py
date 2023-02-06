import hashlib
import re
import json
from django.conf import settings
from robot.smelter.protos.tables_pb2 import TFeedTable


# The idea behind this is to implement stub YT client which would return results for pre-defined tables

XOR_SEED = 0x12345678
BASE_TIME = 1657092839
MULTIBOBA_TIME_DELAY = 300
CRAWL_ADD_TIME_DELAY = 10
LAST_ACCESS_TIME_DELAY = 20


def generate_post_url(channel_id, ts):
    return f"https://channel{channel_id}mod{ts%10}.com/source{ts%10}/timestamp{ts}"


class StubYtClient():
    ROWS_INSERTED = {}
    ROWS_FOR_SELECT = {}

    def __init__(self, empty=False, first_timestamp=1650000000, last_timestamp=1650000042, timestamp_step=1, rows_per_select=settings.MAX_ROWS_PER_SELECT,
                 channel_id=1, is_present_in_channel_query=True, reset_select_rows=False, return_inserted_rows=False):
        self.empty = empty
        self.first_timestamp = first_timestamp
        self.last_timestamp = last_timestamp
        self.timestamp_step = timestamp_step
        self.rows_per_select = rows_per_select
        self.channel_id = channel_id
        self.is_present_in_channel_query = is_present_in_channel_query
        self.reset_select_rows = reset_select_rows
        self.return_inserted_rows = return_inserted_rows

    @staticmethod
    def clear():
        StubYtClient.ROWS_INSERTED.clear()
        StubYtClient.ROWS_FOR_SELECT.clear()

    def lookup_rows(self, table_path, keys, **kwargs):
        if self.empty:
            return []

        if self.return_inserted_rows and table_path in self.ROWS_INSERTED:
            for row in self.ROWS_INSERTED[table_path]:
                yield row

        if table_path == settings.CHANNEL_QUERY_TABLE_PATH and self.is_present_in_channel_query:
            for k in keys:
                row = {}
                row.update(k)
                row["QueryParamsVersion"] = 0
                yield row
        elif table_path == settings.CHANNEL_INFO_TABLE_PATH:
            for k in keys:
                row = {}
                row.update(k)
                row["TotalLikes"] = 42
                row["TotalViews"] = 7500
                yield row
        elif table_path == settings.FEEDS_TABLE_PATH:
            for k in keys:
                post_timestamp = -k["NegPostTimestamp"]
                if self.first_timestamp < post_timestamp and post_timestamp <= self.last_timestamp:
                    yield k
                elif kwargs.get("keep_missing_rows"):
                    yield {}

    def select_rows(self, query):
        if self.empty:
            return []

        table_path = re.match(".*from \\[(.*)\\]", query).groups(0)[0]
        if table_path in self.ROWS_FOR_SELECT:
            for row in self.ROWS_FOR_SELECT[table_path]:
                yield row

        if table_path == settings.FEEDS_TABLE_PATH:
            first_timestamp = max(self.first_timestamp, self.last_timestamp - self.rows_per_select * self.timestamp_step)
            for ts in range(self.last_timestamp, first_timestamp, -self.timestamp_step):
                enrichment_attrs = TFeedTable.TExtraEnrichmentAttrs()
                enrichment_attrs.MultibobaSentimentTime = ts + MULTIBOBA_TIME_DELAY

                content_attrs = TFeedTable.TExtraContentAttrs()
                content_attrs.CrawlAddTime = ts + CRAWL_ADD_TIME_DELAY
                content_attrs.LastAccess = ts + LAST_ACCESS_TIME_DELAY
                yield {
                    "ChannelId": self.channel_id,
                    "NegQueryParamsVersion": 0,
                    "NegPostTimestamp": -ts,
                    "Url": generate_post_url(self.channel_id, ts),
                    "Snippet": hashlib.md5(f"snippet for {ts}".encode("utf-8")).hexdigest(),
                    "Title": hashlib.md5(f"title for {ts}".encode("utf-8")).hexdigest(),
                    "SourceUrl": f"https://channel{self.channel_id}/source{ts%10}",
                    "SourceName": f"Mod{ts%10}",
                    "TextLanguage": 0,
                    "TitleLanguage": 0,
                    "TitleLanguage": 0,
                    "Simhash": ts ^ XOR_SEED,
                    "ExtraContentAttrs": content_attrs.SerializeToString(),
                    "ExtraEnrichmentAttrs": enrichment_attrs.SerializeToString(),
                    "MultibobaSentiment": json.dumps({"Scores": [0, ts % 2, 1 - ts % 2]})
                }

            if not self.reset_select_rows:
                self.last_timestamp = first_timestamp

    def insert_rows(self, table_path, rows):
        if table_path not in self.ROWS_INSERTED:
            self.ROWS_INSERTED[table_path] = []
        self.ROWS_INSERTED[table_path].extend(rows)


def make_stub_yt_client_creator(**kwargs):
    def creator(*inner_args, **inner_kwargs):
        return StubYtClient(**kwargs)
    return creator


def empty_chyt_execute(query, client=None, settings=None):
    return []
