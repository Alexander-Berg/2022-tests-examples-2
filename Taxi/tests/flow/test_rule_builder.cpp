#include <gtest/gtest.h>

#include <google/protobuf/util/json_util.h>
#include <google/protobuf/util/message_differencer.h>

#include <userver/formats/bson/serialize.hpp>
#include <userver/formats/json/serialize.hpp>

#include <flow/rule_builder.hpp>

namespace dorblu {

TEST(TestRuleBuilder, TestEmpty) {}

TEST(TestRuleBuilder, Test1) {
  auto rawString = R"body(
[
			{
				"filter" : {
					"type" : "And",
					"children" : [
						{
							"operand" : "dorblu.taxi.tst.yandex.net",
							"field" : "http_host",
							"type" : "Equals"
						},
						{
							"operand" : "GET",
							"field" : "request_method",
							"type" : "Equals"
						},
						{
							"type" : "Or",
							"children" : [
								{
									"operand" : "/ping",
									"field" : "request_url",
									"type" : "Equals"
								},
								{
									"operand" : "/ping/",
									"field" : "request_url",
									"type" : "Equals"
								},
								{
									"operand" : "/ping?",
									"field" : "request_url",
									"type" : "StartsWith"
								},
								{
									"operand" : "/ping/?",
									"field" : "request_url",
									"type" : "StartsWith"
								}
							]
						}
					]
				},
				"Options" : {
					"CustomHttp" : [
						400,
						401,
						403,
						404,
						429
					]
				},
				"name" : "dorblu.taxi.tst.yandex.net/ping_GET",
				"rule_id" : 0
			},
			{
				"filter" : {
					"type" : "And",
					"children" : [
						{
							"operand" : "dorblu.taxi.tst.yandex.net",
							"field" : "http_host",
							"type" : "Equals"
						}
					]
				},
				"Options" : {
					"CustomHttp" : [
						400,
						401,
						403,
						404,
						429
					]
				},
				"name" : "dorblu.taxi.tst.yandex.net",
				"rule_id" : 1
			},
			{
				"filter" : {
					"type" : "Dummy"
				},
				"name" : "TOTAL",
				"rule_id" : 2
			}
		]
)body";
  auto parsedRules = formats::bson::ArrayFromJsonString(rawString);
  auto result = dorblu::flow::BuildRules(parsedRules);
  ASSERT_EQ(result.size(), 3);

  auto rule1_raw = R"rule(
  {
    "name": "dorblu.taxi.tst.yandex.net/ping_GET",
    "stats": {
      "timings": [
        {
          "type": "req",
          "prefix": "maps_ok_request_timings"
        },
        {
          "type": "ups",
          "prefix": "maps_ok_upstream_timings"
        },
        {
          "type": "ssl",
          "prefix": "maps_ok_ssl_timings"
        }
      ],
                    'requests': [
                        {
                            'first': 400,
                            'last': 400,
                            'count': '0',
                            'prefix': 'maps_400_rps.rps',
                        },
                        {
                            'first': 401,
                            'last': 401,
                            'count': '0',
                            'prefix': 'maps_401_rps.rps',
                        },
                        {
                            'first': 404,
                            'last': 404,
                            'count': '0',
                            'prefix': 'maps_404_rps.rps',
                        },
                        {
                            'first': 499,
                            'last': 499,
                            'count': '0',
                            'prefix': 'maps_timeouts_rps.rps',
                        },
                        {
                            'first': 500,
                            'last': 599,
                            'count': '0',
                            'prefix': 'maps_errors_rps.rps',
                        },
                        {
                            'first': 200,
                            'last': 299,
                            'count': '0',
                            'prefix': 'maps_ok_rps.rps',
                        },
                        {
                            'first': 400,
                            'last': 400,
                            'count': '0',
                            'prefix': 'maps_errors_400_rps.rps',
                        },
                        {
                            'first': 401,
                            'last': 401,
                            'count': '0',
                            'prefix': 'maps_errors_401_rps.rps',
                        },
                        {
                            'first': 403,
                            'last': 403,
                            'count': '0',
                            'prefix': 'maps_errors_403_rps.rps',
                        },
                        {
                            'first': 404,
                            'last': 404,
                            'count': '0',
                            'prefix': 'maps_errors_404_rps.rps',
                        },
                        {
                            'first': 429,
                            'last': 429,
                            'count': '0',
                            'prefix': 'maps_errors_429_rps.rps',
                        },
      ],
                    'bytesCounters': [{'prefix': 'bps.bps', 'counter': '0'}],
                    'cacheRates': [
                        {
                            'prefix': 'cache',
                            'entries': [
                                {'cacheStatus': 'HIT', 'count': '0'},
                                {'cacheStatus': 'MISS', 'count': '0'},
                                {'cacheStatus': 'EXPIRED', 'count': '0'},
                                {'cacheStatus': 'BYPASS', 'count': '0'},
                                {'cacheStatus': 'STALE', 'count': '0'},
                                {'cacheStatus': 'UPDATING', 'count': '0'},
                                {'cacheStatus': 'REVALIDATED', 'count': '0'},
                                {'cacheStatus': 'NONE', 'count': '0'},
                            ],
                        },
                    ],
    },
    "filter": {
      "type": "And",
      "children": [
        {
          "operand" : "dorblu.taxi.tst.yandex.net",
          "field_name" : "http_host",
          "type" : "Equals"
        },
        {
          "operand" : "GET",
          "field_name" : "request_method",
          "type" : "Equals"
        },
        {
          "type" : "Or",
          "children": [
								{
									"operand" : "/ping",
									"field_name" : "request_url",
									"type" : "Equals"
								},
								{
									"operand" : "/ping/",
									"field_name" : "request_url",
									"type" : "Equals"
								},
								{
									"operand" : "/ping?",
									"field_name" : "request_url",
									"type" : "StartsWith"
								},
								{
									"operand" : "/ping/?",
									"field_name" : "request_url",
									"type" : "StartsWith"
								}
          ]
        }
      ]
    }
  }
  )rule";
  DorBluPB::Rule rule1_pb;
  auto ok = google::protobuf::util::JsonStringToMessage(rule1_raw, &rule1_pb);
  ASSERT_TRUE(ok.ok());
  google::protobuf::string buf;
  google::protobuf::util::MessageDifferencer m;
  m.ReportDifferencesToString(&buf);
  m.Compare(result[0], rule1_pb);
  EXPECT_TRUE(m.Compare(result[0], rule1_pb)) << buf;
}

}  // namespace dorblu
