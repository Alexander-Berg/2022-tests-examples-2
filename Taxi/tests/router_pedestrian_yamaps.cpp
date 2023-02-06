#include <gtest/gtest.h>

#include <clients/graphite.hpp>
#include <clients/router_exceptions.hpp>
#include <clients/router_pedestrian_yamaps.hpp>
#include <common/test_config.hpp>
#include <threads/async.hpp>
#include <utils/file_system.hpp>

namespace {

const clients::Graphite& graphite() {
  static const clients::Graphite client;
  return client;
}

const utils::http::Client& http_client() {
  static utils::Async async(1, "test_async", false);
  static const utils::http::Client client(async, 1, "test_http_client", false);
  return client;
}

using clients::routing::BadResponseError;
using clients::routing::InsolubleRequestError;
using clients::routing::path_t;
using clients::routing::RoutePedestrianInfo;
using clients::routing::RouterPedestrianYaMaps;

}  // namespace

TEST(RouterPedestrianYamaps, MakeQueryUrl) {
  const std::string& expected_url =
      "http://core-masstransit-router.maps.yandex.net/pedestrian/"
      "route?lang=ru-RU&origin=yataxi&rll=-1.4,2.4~3.4,-7.4";
  RouterPedestrianYaMaps router(http_client(), graphite());

  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  path_t path;
  path.emplace_back(-1.4, 2.4);
  path.emplace_back(3.4, -7.4);
  const std::string& actual_url =
      router.MakeQueryUrl(path, config.Get<config::PedestrianRouter>(), {});
  EXPECT_EQ(expected_url, actual_url);
}

TEST(RouterPedestrianYamaps, MakeBulkQueryUrl) {
  const std::string& expected_url =
      "http://core-masstransit-router.maps.yandex.net/pedestrian/matrix?"
      "lang=ru-RU&origin=yataxi&srcll=-1.4,2.4~3.4,-7.4&dstll=-1.4,2.4~3.4,-7."
      "4";
  RouterPedestrianYaMaps router(http_client(), graphite());

  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  path_t path;
  path.emplace_back(-1.4, 2.4);
  path.emplace_back(3.4, -7.4);
  const std::string& actual_url = router.MakeBulkQueryUrl(
      path, path, config.Get<config::PedestrianRouter>(), {});
  EXPECT_EQ(expected_url, actual_url);
}

TEST(RouterPedestrianYamaps, ParseNoPath) {
  const auto& file_body = utils::ReadFile(
      SOURCE_DIR "/tests/static/router_pedestrian_yamaps_no_path.bin");
  ASSERT_FALSE(file_body.empty());

  EXPECT_THROW(RouterPedestrianYaMaps::Parse(file_body, {}),
               InsolubleRequestError);
}

class RouterPedestrianYamapsParseWithFilenameParam
    : public ::testing::Test,
      public ::testing::WithParamInterface<const char*> {};

TEST_P(RouterPedestrianYamapsParseWithFilenameParam, ParseValid) {
  const auto& file_body =
      utils::ReadFile(std::string(SOURCE_DIR "/tests/static/") + GetParam());
  ASSERT_FALSE(file_body.empty());

  RoutePedestrianInfo ri = RouterPedestrianYaMaps::Parse(file_body, {});

  EXPECT_LT(0.0, ri.total_time);
  EXPECT_LT(0.0, ri.total_distance);
  EXPECT_LE(2U, ri.path.size());
}

INSTANTIATE_TEST_CASE_P(Serial, RouterPedestrianYamapsParseWithFilenameParam,
                        ::testing::Values("router_pedestrian_yamaps_0.bin",
                                          "router_pedestrian_yamaps_1.bin"), );
