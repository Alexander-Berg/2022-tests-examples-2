#include <clients/geotracks.hpp>

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <fstream>

#include <utils/helpers/json.hpp>

namespace clients {
namespace geotracks {
std::vector<utils::geometry::Track> ParseJsonReply(const Json::Value& value,
                                                   size_t output_size,
                                                   const LogExtra& log_extra);
}  // namespace geotracks
}  // namespace clients

TEST(gps_archive, TestParseResponse) {
  std::ifstream input_stream(SOURCE_DIR "/tests/static/geotracks_result.json");
  Json::Value root = utils::helpers::ParseJson(input_stream);
  const auto track = clients::geotracks::ParseJsonReply(root, 4, {});
  ASSERT_FALSE(track.empty());
  ASSERT_FALSE(track[0].empty());
  ASSERT_FALSE(track[2].empty());
  ASSERT_TRUE(track[1].empty());
  ASSERT_TRUE(track[3].empty());
}
