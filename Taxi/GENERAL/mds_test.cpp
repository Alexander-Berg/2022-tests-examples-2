#include <trackstory/mds.hpp>
#include <trackstory/types.hpp>

#include <gtest/gtest.h>
#include <gpssignal/test/gpssignal_plugin_test.hpp>
#include <testing/source_path.hpp>
#include <userver/formats/json.hpp>
#include <userver/fs/blocking/read.hpp>

using gpssignal::test::GpsSignalTestPlugin;

namespace {

using trackstory::mds::Line;
using trackstory::mds::Track;

const double kEpsilon = 0.0001;

std::vector<gpssignal::GpsSignal> TrackFromTestJson(
    const formats::json::Value& js) {
  std::vector<gpssignal::GpsSignal> ret;
  for (const auto& q : js) {
    gpssignal::GpsSignal p;
    p.longitude = q[1].As<double>() * gpssignal::lon;
    p.latitude = q[0].As<double>() * gpssignal::lat;
    p.timestamp =
        trackstory::TimePoint(std::chrono::seconds(q[2].As<uint64_t>()));
    ret.push_back(p);
  }
  return ret;
}

Line ToLine(const Track& track) {
  Line line;
  for (const auto& pos : track) {
    line.push_back(pos);
  }

  return line;
}

}  // namespace

TEST(MdsStorePreprocess, TestSimplifyReal) {
  const auto data = fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/long_track.json"));
  formats::json::Value js = formats::json::FromString(data);

  auto track = TrackFromTestJson(js);
  ASSERT_EQ(track.size(), 10944);

  trackstory::mds::FilterParams filter_params{300, 1000, 5, 3, 0.000001};
  auto result = trackstory::mds::PreprocessData(track, kEpsilon, filter_params);
  ASSERT_TRUE(result.size() < 5000 && result.size() > 100);
}

TEST(MdsStoreMarshall, TestSimple) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      std::nullopt,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};

  Track track{pos};
  auto data = trackstory::mds::MarshallRoute(ToLine(track));
  ASSERT_EQ(data.size(), 80);

  auto track_unmarshalled = trackstory::mds::UnmarshallRoute(data);
  ASSERT_EQ(track_unmarshalled.size(), track.size());
  GpsSignalTestPlugin::TestGpsSignalsAreClose(track_unmarshalled[0], track[0]);
}

TEST(MdsStoreMarshall, TestRealData) {
  const auto data = fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/test_route.fb"));

  auto track = trackstory::mds::UnmarshallRoute(data);
  ASSERT_EQ(track.size(), 10);
}

TEST(MdsStoreMarshall, TestNoOptionals) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      trackstory::TimePoint(std::chrono::milliseconds(111))};

  Track track{pos};
  auto data = trackstory::mds::MarshallRoute(ToLine(track));
  ASSERT_EQ(data.size(), 72);

  auto track_unmarshalled = trackstory::mds::UnmarshallRoute(data);
  ASSERT_EQ(track_unmarshalled.size(), track.size());
  GpsSignalTestPlugin::TestGpsSignalsAreClose(track_unmarshalled[0], track[0]);
}

TEST(MdsStoreMarshall, TestZeroSpeed) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(0.0),
      std::nullopt,
      std::nullopt,
      trackstory::TimePoint(std::chrono::milliseconds(111))};

  Track track{pos};
  auto data = trackstory::mds::MarshallRoute(ToLine(track));
  ASSERT_EQ(data.size(), 72);

  auto track_unmarshalled = trackstory::mds::UnmarshallRoute(data);
  ASSERT_EQ(track_unmarshalled.size(), track.size());
  GpsSignalTestPlugin::TestGpsSignalsAreClose(track_unmarshalled[0], track[0]);
}
