#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/geosuggest/common/objects.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::geosuggest;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("geosuggest_common");
}  // namespace

TEST(Common, AppInfo) {
  const auto app_info = ml::common::FromJsonString<AppInfo>(
      ml::common::ReadFileContents(kTestDataDir + "/app_info.json"));
  ASSERT_EQ(app_info.name, "android");
  ASSERT_EQ(app_info.brand, "yataxi");
  ASSERT_EQ(app_info.platform, "android");
  ASSERT_EQ(app_info.device_make, "xiaomi");
  ASSERT_EQ(app_info.device_model, "mi6plusSmax");
}

TEST(Common, EatsOrder) {
  const auto eats_orders = ml::common::FromJsonString<std::vector<EatsOrder>>(
      ml::common::ReadFileContents(kTestDataDir + "/eats_orders.json"));
  ASSERT_EQ(eats_orders.size(), 1ul);
  ASSERT_EQ(eats_orders[0].order_id, "ailr38y2iu");
  ASSERT_EQ(eats_orders[0].status, "delivered");
  ASSERT_EQ(eats_orders[0].source, "lavka");
  const auto geopoint = ml::common::GeoPoint(37.891, 55.101);
  ASSERT_FLOAT_EQ(eats_orders[0].delivery_location.lon, geopoint.lon);
  ASSERT_FLOAT_EQ(eats_orders[0].delivery_location.lat, geopoint.lat);
  ASSERT_TRUE(eats_orders[0].is_asap);
  ASSERT_EQ(eats_orders[0].delivered,
            ml::common::datetime::Stringtime("2019-12-01T12:29:43.66744+0300"));
  ASSERT_EQ(eats_orders[0].created,
            ml::common::datetime::Stringtime("2019-12-01T12:09:43.66744+0300"));
  ASSERT_EQ(eats_orders[0].cancel_reason, "lolkek");
}
