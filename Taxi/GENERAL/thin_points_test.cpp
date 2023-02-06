#include "thin_points.hpp"

#include <gtest/gtest.h>

#include <models/history_points.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>
#include <utils/enum_helpers.hpp>

using namespace coord_control;
using Minutes = std::chrono::minutes;
using Seconds = std::chrono::seconds;

namespace {
void IsEqual(const models::HistoryPointsMap& lhs,
             const models::HistoryPointsMap& rhs) {
  auto now = ::utils::datetime::Now();
  std::vector<size_t> l_vec;
  for (const auto& [ts, _] : lhs) {
    l_vec.push_back(std::chrono::duration_cast<Seconds>(now - ts).count());
  }
  std::vector<size_t> r_vec;
  for (const auto& [ts, _] : rhs) {
    r_vec.push_back(std::chrono::duration_cast<Seconds>(now - ts).count());
  }
  EXPECT_EQ(l_vec, r_vec);
}

void IsEqual(const models::PointsStorage& lhs,
             const models::PointsStorage& rhs) {
  for (size_t i = 0;
       i < static_cast<size_t>(::geobus::types::SignalV2Source::kCount); ++i) {
    EXPECT_EQ(lhs.points[i].map.size(), rhs.points[i].map.size());
    IsEqual(lhs.points[i].map, rhs.points[i].map);
  }
}
}  // namespace

TEST(ThinPoints, NoLeftPointsEnd) {
  // 2020-05-05T05:05:00
  std::chrono::system_clock::time_point now{Seconds{1588655100}};

  // minutes -> points limit
  const auto history_settings = models::HistorySettings{
      {Minutes(0), 0},  //
      {Minutes(1), 0},  //
      {Minutes(3), 3},  //
  };

  auto history_points_map = models::HistoryPointsMap{
      {now - Seconds(20), {}},   //
      {now - Seconds(40), {}},   //
      {now - Seconds(60), {}},   //
      {now - Seconds(100), {}},  //
      {now - Seconds(140), {}},  //
      {now - Seconds(180), {}},  //
  };

  ::utils::datetime::MockNowSet(now += Seconds(30));
  coord_control::algorithms::ThinPointsAlgorithm(history_points_map,
                                                 history_settings);

  IsEqual(history_points_map, models::HistoryPointsMap({
                                  {now - Seconds(50), {}},   //
                                  {now - Seconds(90), {}},   //
                                  {now - Seconds(130), {}},  //
                                  {now - Seconds(170), {}},  //
                              }));

  ::utils::datetime::MockNowSet(now += Seconds(30));
  coord_control::algorithms::ThinPointsAlgorithm(history_points_map,
                                                 history_settings);
  IsEqual(history_points_map, models::HistoryPointsMap({
                                  {now - Seconds(80), {}},   //
                                  {now - Seconds(120), {}},  //
                                  {now - Seconds(160), {}},  //
                              }));
}

TEST(ThinPoints, WithLeftPointsEnd) {
  // 2020-05-05T05:05:00
  std::chrono::system_clock::time_point now{Seconds{1588655100}};

  // minutes -> points limit
  const auto history_settings = models::HistorySettings{
      {Minutes(0), 0},  //
      {Minutes(1), 0},  ///
      {Minutes(3), 3},  //
      {Minutes(6), 3},  //
  };

  auto history_points_map = models::HistoryPointsMap{
      {now - Seconds(20), {}},   //
      {now - Seconds(40), {}},   //
      {now - Seconds(60), {}},   //
      {now - Seconds(100), {}},  //
      {now - Seconds(140), {}},  //
      {now - Seconds(180), {}},  //
      {now - Seconds(240), {}},  //
      {now - Seconds(300), {}},  //
      {now - Seconds(360), {}},  //
  };

  ::utils::datetime::MockNowSet(now += Seconds(30));

  coord_control::algorithms::ThinPointsAlgorithm(history_points_map,
                                                 history_settings);

  IsEqual(history_points_map, models::HistoryPointsMap({
                                  {now - Seconds(50), {}},   //
                                  {now - Seconds(90), {}},   //
                                  {now - Seconds(130), {}},  //
                                  {now - Seconds(170), {}},  //
                                  {now - Seconds(210), {}},  //
                                  {now - Seconds(270), {}},  //
                                  {now - Seconds(330), {}},  //
                              }));

  ::utils::datetime::MockNowSet(now += Seconds(30));
  coord_control::algorithms::ThinPointsAlgorithm(history_points_map,
                                                 history_settings);
  IsEqual(history_points_map, models::HistoryPointsMap({
                                  {now - Seconds(80), {}},   //
                                  {now - Seconds(120), {}},  //
                                  {now - Seconds(160), {}},  //
                                  {now - Seconds(200), {}},  //
                                  {now - Seconds(240), {}},  //
                                  {now - Seconds(300), {}},  //
                              }));
}

TEST(ThinPoints, Fallback) {
  // 2020-05-05T05:05:00
  std::chrono::system_clock::time_point now{Seconds{1588655100}};
  ::utils::datetime::MockNowSet(now);

  models::PointsStorage history_points;
  history_points.points[0].map = {
      {now - Seconds(20), {}},   //
      {now - Seconds(40), {}},   //
      {now - Seconds(300), {}},  //
      {now - Seconds(380), {}},  //
  };
  history_points.points[1].map = {
      {now - Seconds(30), {}},   //
      {now - Seconds(240), {}},  //
      {now - Seconds(300), {}},  //
      {now - Seconds(380), {}},  //
  };

  models::PointsStorage history_points_after_thin;
  history_points_after_thin.points[0].map = {
      {now - Seconds(20), {}},   //
      {now - Seconds(40), {}},   //
      {now - Seconds(300), {}},  //
  };
  history_points_after_thin.points[1].map = {
      {now - Seconds(30), {}},   //
      {now - Seconds(240), {}},  //
      {now - Seconds(300), {}},  //
  };

  for (size_t i = 0;
       i < coord_control::utils::Index(geobus::types::SignalV2Source::kCount);
       ++i) {
    coord_control::algorithms::FallbackThinPointsAlgorithm(
        history_points.points[i].map, std::chrono::minutes{5});
  }
  IsEqual(history_points, history_points_after_thin);
}
