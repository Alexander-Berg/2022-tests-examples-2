#include <gtest/gtest.h>
#include <fstream>
#include <utils/datetime.hpp>
#include <utils/helpers/json.hpp>
#include "clients/routehistory/models.hpp"
#include "clients/routehistory/parsers.hpp"

namespace Json {
void PrintTo(const Json::Value& json, std::ostream* os) {
  *os << utils::helpers::WriteJson(json, true);
}
}  // namespace Json

namespace clients::routehistory::test {

Json::Value LoadJson(const std::string& filename) {
  std::ifstream input_stream(SOURCE_DIR "/tests/static/" + filename);
  return utils::helpers::ParseJson(input_stream);
}

TEST(RouteHistory, SerializeRequest1) {
  RoutehistoryGetRequest request{};
  request.created_since =
      utils::datetime::Stringtime("2016-11-05T10:00:00+0000");
  request.position = Point{37.0, 55.0};
  request.max_distance = 1000.0;
  request.max_records_to_inspect = 3;
  request.max_results = 2;
  request.sort_by = SortMode::kDistance;
  auto json = Serialize(request);
  auto expected_json = LoadJson("sample_request1.json");
  EXPECT_EQ(json, expected_json);
}

TEST(RouteHistory, SerializeRequest2) {
  RoutehistoryGetRequest request{};
  request.sort_by = SortMode::kTime;
  auto json = Serialize(request);
  auto expected_json = LoadJson("sample_request2.json");
  EXPECT_EQ(json, expected_json);
}

TEST(RouteHistory, ParseResponse1) {
  using namespace std::string_literals;
  auto json = LoadJson("sample_response.json");
  auto r = Parse<RouteHistoryGetResponse>(json);
  EXPECT_EQ(r.results.size(), 2u);
  EXPECT_EQ(r.results.at(0).id, "id3");
  EXPECT_EQ(r.results.at(0).comment, boost::none);
  EXPECT_EQ(r.results.at(0).created,
            utils::datetime::Stringtime("2020-03-01T00:00:00+0000"));
  EXPECT_EQ(r.results.at(0).route.source.type, "address"s);
  EXPECT_EQ(r.results.at(0).route.source.object_type, "другое"s);
  EXPECT_EQ(r.results.at(0).route.source.country, "ru"s);
  EXPECT_EQ(r.results.at(0).route.source.point, Point(39.0, 57.0));
  EXPECT_EQ(r.results.at(0).route.source.full_text, "full text 5"s);
  EXPECT_EQ(r.results.at(0).route.source.porchnumber, "5"s);
  EXPECT_EQ(r.results.at(0).route.source.exact, true);
  EXPECT_EQ(r.results.at(0).route.source.uri, "ymapsbm1://sample_uri_1"s);
  EXPECT_EQ(r.results.at(0).route.source.metrica_method, "method2"s);
  EXPECT_EQ(r.results.at(0).route.source.metrica_action, "action2"s);
  EXPECT_EQ(r.results.at(0).route.destinations.value().size(), 2u);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).type, "address"s);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).object_type,
            "другое"s);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).country, "ru"s);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).point,
            Point(40.5, 60.0));
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).full_text,
            "full text 3"s);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).porchnumber,
            boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).exact, true);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).uri, boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).metrica_method,
            "method3"s);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(0).metrica_action,
            "action3"s);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).type, boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).object_type,
            boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).country,
            boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).point,
            Point(50.0, 61.31));
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).full_text,
            "b_full"s);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).porchnumber,
            boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).exact,
            boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).uri, boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).metrica_method,
            boost::none);
  EXPECT_EQ(r.results.at(0).route.destinations.value().at(1).metrica_action,
            boost::none);
  EXPECT_EQ(r.results.at(0).brand, "yango");
  EXPECT_EQ(r.results.at(0).completion_point, Point(15.2, 16.4));
  EXPECT_EQ(r.results.at(0).adjusted_source, Point(10.1, 20.1));
  EXPECT_EQ(r.results.at(1).id, "id2");
  EXPECT_EQ(r.results.at(1).comment, "test"s);
  EXPECT_EQ(r.results.at(1).created,
            utils::datetime::Stringtime("2019-04-01T00:00:00+0000"));
  EXPECT_EQ(r.results.at(1).route.source.type, "address"s);
  EXPECT_EQ(r.results.at(1).route.source.object_type, boost::none);
  EXPECT_EQ(r.results.at(1).route.source.country, "Россия"s);
  EXPECT_EQ(r.results.at(1).route.source.point, Point(39.0, 57.0));
  EXPECT_EQ(r.results.at(1).route.source.full_text, "full text 2"s);
  EXPECT_EQ(r.results.at(1).route.source.porchnumber, "5"s);
  EXPECT_EQ(r.results.at(1).route.source.exact, false);
  EXPECT_EQ(r.results.at(1).route.source.uri, "ymapsbm1://sample_uri_1"s);
  EXPECT_EQ(r.results.at(1).route.source.metrica_method, "method2"s);
  EXPECT_EQ(r.results.at(1).route.source.metrica_action, "action2"s);
  EXPECT_EQ(r.results.at(1).route.destinations, boost::none);
  EXPECT_EQ(r.results.at(1).brand, "yango");
  EXPECT_EQ(r.results.at(1).completion_point, boost::none);
  EXPECT_EQ(r.results.at(1).adjusted_source, boost::none);
}

std::string ParseBadResponse(const Json::Value& json) {
  std::string result;
  try {
    Parse<RouteHistoryGetResponse>(json);
  } catch (const JsonParseException& ex) {
    result = ex.what();
  }
  return result;
}

TEST(RouteHistory, ParseBadResponse1) {
  EXPECT_EQ(
      ParseBadResponse(LoadJson("bad_response1.json")),
      "<root>.results[0].completion_point[0]: wrong type, expected double");
}

TEST(RouteHistory, ParseBadResponse2) {
  EXPECT_EQ(ParseBadResponse(LoadJson("bad_response2.json")),
            "<root>.results[0].created: Can't parse datetime: bad date");
}

TEST(RouteHistory, ParseBadResponse3) {
  EXPECT_EQ(ParseBadResponse(LoadJson("bad_response3.json")),
            "<root>.results[0].route.source.type: wrong type, expected string");
}

TEST(RouteHistory, ParseEmptyResponse1) {
  EXPECT_EQ(ParseBadResponse(Json::nullValue),
            "<root>.results: wrong type, expected array");
}

TEST(RouteHistory, ParseEmptyResponse2) {
  EXPECT_EQ(ParseBadResponse(Json::objectValue),
            "<root>.results: wrong type, expected array");
}

TEST(RouteHistory, ParseEmptyResponse3) {
  EXPECT_EQ(ParseBadResponse(Json::arrayValue),
            "<root>.results: in Json::Value::find(key, end, found): requires "
            "objectValue or nullValue");
}

}  // namespace clients::routehistory::test
