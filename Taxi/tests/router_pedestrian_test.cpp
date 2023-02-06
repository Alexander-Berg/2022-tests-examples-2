#include <clients/router_pedestrian_fallback.hpp>
#include <clients/router_pedestrian_yamaps.hpp>

#include <fstream>
#include <sstream>

#include <google/protobuf/message.h>
#include <gtest/gtest.h>

#include <common/mock_handlers_context.hpp>

using ::testing::Values;
using namespace clients::routing;

class YaMapsPedestrianRouterMNTestParseWithFilenameParam
    : public ::testing::Test,
      public ::testing::WithParamInterface<
          std::tuple<std::string, std::vector<BulkPedestrianInfo>>> {};

TEST_P(YaMapsPedestrianRouterMNTestParseWithFilenameParam, ParseValidDocument) {
  std::string input_file(SOURCE_DIR "/tests/static/");
  input_file += '/';
  input_file += std::get<0>(GetParam());
  std::ifstream input_stream(input_file);
  std::string file_contents;
  file_contents.assign((std::istreambuf_iterator<char>(input_stream)),
                       std::istreambuf_iterator<char>());

  std::vector<BulkPedestrianInfo> parsed{
      RouterPedestrianYaMaps::ParseBulk(file_contents, {})};

  std::vector<BulkPedestrianInfo> expected_result = std::get<1>(GetParam());

  EXPECT_EQ(expected_result.size(), parsed.size());
  for (size_t i = 0; i < parsed.size(); ++i) {
    EXPECT_EQ(expected_result[i].from_idx, parsed[i].from_idx);
    EXPECT_EQ(expected_result[i].to_idx, parsed[i].to_idx);
    EXPECT_EQ(expected_result[i].total_time, parsed[i].total_time);
    EXPECT_EQ(expected_result[i].total_distance, parsed[i].total_distance);
  }
}

INSTANTIATE_TEST_CASE_P(
    TestRoutePedestrianParsing,
    YaMapsPedestrianRouterMNTestParseWithFilenameParam,
    Values(std::make_tuple("yamaps_router_pedestrian_mn.bin",
                           std::vector<BulkPedestrianInfo>(
                               {BulkPedestrianInfo(0, 0, 2, 3),
                                BulkPedestrianInfo(0, 1, 8, 11),
                                BulkPedestrianInfo(1, 0, 8, 11),
                                BulkPedestrianInfo(1, 1, 2, 3)})),
           std::make_tuple("yamaps_router_pedestrian_mn_no_route.bin",
                           std::vector<BulkPedestrianInfo>(
                               {BulkPedestrianInfo(1, 0, 8, 11),
                                BulkPedestrianInfo(1, 1, 2, 3)}))), );

class RouterPedestrianFallbackTest : public ::testing::Test,
                                     public MockHeadersContext {};

TEST_F(RouterPedestrianFallbackTest, Route) {
  static const double kAbsError = 0.001;

  RouterPedestrianFallback router;
  path_t path = {{37.0, 55.0}, {37.1, 55.0}, {37.1, 55.1}, {37.0, 55.0}};

  RoutePedestrianInfo result = router.RouteEx(path, GetContext(), {});

  EXPECT_NEAR(30320.708, result.total_distance, kAbsError);
  EXPECT_NEAR(21830.91, result.total_time, kAbsError);
}
