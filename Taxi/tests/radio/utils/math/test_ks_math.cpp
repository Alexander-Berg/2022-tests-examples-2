#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/parse/common_containers.hpp>

#include <radio/blocks/utils/math/ks.hpp>

#include "../../../tools/testutils.hpp"

namespace hejmdal::utils::math {

TEST(TestKsMath, DataFromFile) {
  auto json_test_data = formats::json::blocking::FromFile(
      testutils::kStasticDir + "/ks_test_inputs/ks_test_data.json");

  for (const auto& elem : json_test_data) {
    auto window = elem["window"].As<std::vector<double>>();
    auto window2 = elem["window2"].As<std::vector<double>>();
    auto expected_d = elem["d"].As<double>();
    auto expected_p = elem["p"].As<double>();

    auto test_value = KsTest2Samples(window, window2);
    EXPECT_DOUBLE_EQ(expected_d, test_value.ks_statistics);
    // this fails for 1e-16, but we consider 1e-15 good enough
    EXPECT_NEAR(expected_p, test_value.p_value, 1e-15);
  }
}

}  // namespace hejmdal::utils::math
