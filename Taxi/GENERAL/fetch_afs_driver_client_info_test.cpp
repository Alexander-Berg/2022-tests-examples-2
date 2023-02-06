#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>
#include "fetch_afs_driver_client_info.hpp"

namespace cf = candidates::filters;
const cf::FilterInfo kEmptyInfo;
const candidates::GeoMember kMember;

TEST(FetchAfsDriverClientInfoTest, Base) {
  const auto make_context = [](const std::string& id) {
    cf::Context context;
    {
      auto driver = models::UniqueDriver{id, {}, 0, {}, std::nullopt};
      cf::infrastructure::FetchUniqueDriver::Set(
          context, std::make_shared<models::UniqueDriver>(std::move(driver)));
    }
    return context;
  };

  const auto test = [&make_context](const std::string& id, bool check) {
    auto context = make_context("id1");

    models::AfsDriverClientInfoMap driver_client_info_map{{id, {"fake_gps"}}};
    cf::infrastructure::FetchAfsDriverClientInfo filter(
        kEmptyInfo, std::make_shared<models::AfsDriverClientInfoMap>(
                        std::move(driver_client_info_map)));

    EXPECT_EQ(filter.Process(kMember, context), cf::Result::kAllow);

    const auto p =
        cf::infrastructure::FetchAfsDriverClientInfo::TryGet(context);

    if (check) {
      EXPECT_NE(p, nullptr);
    } else {
      EXPECT_EQ(p, nullptr);
    }
  };

  test("id1", true);
  test("id2", false);
}
