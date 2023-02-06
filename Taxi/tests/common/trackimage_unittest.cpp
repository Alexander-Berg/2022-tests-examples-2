#include <gtest/gtest.h>

#include <common/track_image.hpp>
#include <utils/helpers/json.hpp>
#include "utils/jsonfixtures.hpp"

using namespace utils::helpers;
using namespace utils::geometry;

TEST(TrackImage, Bbox) {
  Track track = {{6.0, 6.0},   {12.0, 6.0},  {6.0, 18.0},
                 {12.0, 18.0}, {12.0, 24.0}, {6.0, 12.0}};

  config::BboxDelta delta(0.1, 0.2, 0.3, 0.4);
  BBox bbox = common::track_image::CalculateBbox(
      std::vector<utils::geometry::Point>(), track, delta);

  const double width = 12.0 - 6.0;
  const double height = 24.0 - 6.0;
  EXPECT_DOUBLE_EQ(6.0 - width * delta.left, bbox.bl.lon);
  EXPECT_DOUBLE_EQ(6.0 - height * delta.bottom, bbox.bl.lat);
  EXPECT_DOUBLE_EQ(12.0 + width * delta.right, bbox.tr.lon);
  EXPECT_DOUBLE_EQ(24.0 + height * delta.top, bbox.tr.lat);
}

namespace clients {
namespace geotracks {
utils::geometry::Track ParseJsonTrack(const Json::Value& js_track);
}
}  // namespace clients

TEST(TrackImage, TracksFromGeotracks) {
  const Json::Value& json_body =
      JSONFixtures::GetFixtureJSON("geotracks-response.json");
  Json::Value tracks_json = json_body["tracks"];
  EXPECT_TRUE(tracks_json.isArray());
  EXPECT_FALSE(tracks_json.empty());

  // parse taximeter response
  std::vector<utils::geometry::Track> tracks;
  tracks.reserve(tracks_json.size());
  for (const Json::Value& json : tracks_json) {
    auto response = clients::geotracks::ParseJsonTrack(json["track"]);
    tracks.emplace_back(response);
  }

  EXPECT_EQ(1u, tracks.size());
  auto simplified_track =
      common::track_image::SimplifyTrack(tracks[0], 13 + 8, 100);

  EXPECT_EQ(simplified_track.size(), 100u);
  EXPECT_DOUBLE_EQ(simplified_track.front().lon, tracks[0].front().lon);
  EXPECT_DOUBLE_EQ(simplified_track.front().lat, tracks[0].front().lat);
}
