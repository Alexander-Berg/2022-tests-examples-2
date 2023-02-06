#include <userver/utest/utest.hpp>

#include <endpoints/full/plugins/mock_eta/eta_approximation.hpp>

namespace routestats::full {

TEST(GetTimeSinceMidnight, FromString) {
  ASSERT_EQ(GetTimeSinceMidnight("10:00:00").count(), 36000);
  ASSERT_EQ(GetTimeSinceMidnight("00:00:00").count(), 0);
  ASSERT_EQ(GetTimeSinceMidnight("24:00:00").count(), 0);
}

TEST(GetDiffAsDouble, BaseCase) {
  auto minuend = GetTimeSinceMidnight("10:00:00");
  auto subtrahend = GetTimeSinceMidnight("05:00:00");
  ASSERT_EQ(GetDiffAsDouble(minuend, subtrahend), 5 * 3600);
  minuend = GetTimeSinceMidnight("03:00:00");
  subtrahend = GetTimeSinceMidnight("15:00:00");
  ASSERT_EQ(GetDiffAsDouble(minuend, subtrahend), 12 * 3600);
}

TEST(CalcMean, BaseCase) {
  auto left = experiments3::mock_eta::EtaApproximation{"10:00:00", std::nullopt,
                                                       300, 20};
  auto right = experiments3::mock_eta::EtaApproximation{"16:00:00",
                                                        std::nullopt, 900, 20};
  auto now = GetTimeSinceMidnight("12:00:00");
  ASSERT_EQ(CalcMean(left, right, now), 500);
  now = GetTimeSinceMidnight("22:00:00");
  ASSERT_EQ(CalcMean(right, left, now), 700);
}

std::vector<int> FormEtaSequence(
    double mean, bool use_geohash, int geohash_precision,
    const std::optional<std::string>& phone_id,
    const std::optional<geometry::Position>& position,
    const experiments3::mock_eta::EtaApproximation& eta_approximation,
    std::size_t size) {
  std::vector<int> result(size);
  for (std::size_t i = 0; i < size; ++i) {
    const auto duration = GenerateDuration(
        use_geohash, geohash_precision, phone_id, position, eta_approximation);
    result[i] = static_cast<int>(AddNoiseToEta(mean, eta_approximation.std_sec,
                                               TimeSinceMidnight{i}, duration));
  }
  return result;
}

bool CheckEtaSequence(const std::vector<int>& sequence, int min_duration) {
  if (sequence.empty()) {
    return true;
  }
  int current_min_duration = sequence.size();
  int last_eta = sequence[0];
  int duration = 1;
  for (std::size_t i = 1; i < sequence.size(); ++i) {
    if (sequence[i] != last_eta) {
      current_min_duration = std::min(duration, current_min_duration);
      duration = 1;
      last_eta = sequence[i];
    } else {
      duration++;
    }
  }
  // we does not consider last serie
  // current_min_duration = std::min(duration, current_min_duration);
  return current_min_duration >= min_duration;
}

TEST(AddNoiseToEta, BaseCase) {
  experiments3::mock_eta::EtaApproximation eta_approximation{
      /*time_point*/ "10:00:00", /*seed*/ std::nullopt,
      /*mean_sec*/ 300,          /*std_sec*/ 20,
      /*min_value_sec*/ 10,      /*max_value_sec*/ 600,
      /*duration_hint*/ 58};
  const auto eta_sequence1 = FormEtaSequence(
      60., true, 8, "phone_id",
      geometry::Position{0.0 * geometry::lon, 0.0 * geometry::lat},
      eta_approximation, 24 * 60 * 60);
  ASSERT_TRUE(CheckEtaSequence(eta_sequence1, eta_approximation.duration_hint));

  const auto eta_sequence2 = FormEtaSequence(
      60., false, 8, "phone_id",
      geometry::Position{0.0 * geometry::lon, 0.0 * geometry::lat},
      eta_approximation, 24 * 60 * 60);
  ASSERT_TRUE(CheckEtaSequence(eta_sequence2, eta_approximation.duration_hint));

  const auto eta_sequence3 = FormEtaSequence(
      60., true, 8, std::nullopt,
      geometry::Position{0.0 * geometry::lon, 0.0 * geometry::lat},
      eta_approximation, 24 * 60 * 60);
  ASSERT_TRUE(CheckEtaSequence(eta_sequence3, eta_approximation.duration_hint));
}

}  // namespace routestats::full
