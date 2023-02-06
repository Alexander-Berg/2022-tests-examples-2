#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include "license_id.hpp"

namespace cf = candidates::filters;

namespace {

cf::Context CreateContext(const std::string& dbid_uuid,
                          const std::string& license_id) {
  cf::Context context;
  models::Driver driver;
  driver.id = models::DriverId::FromDbidUuid(dbid_uuid);
  driver.license_id = license_id;
  cf::infrastructure::FetchDriver::Set(
      context, std::make_shared<const models::Driver>(std::move(driver)));
  return context;
}

const cf::FilterInfo kEmptyInfo;

}  // namespace

TEST(LicenseIdFilter, Basic) {
  std::unordered_set<std::string> excluded_license_ids{"license_id1",
                                                       "license_id2"};

  cf::infrastructure::LicenseId filter(kEmptyInfo,
                                       std::move(excluded_license_ids));
  candidates::GeoMember driver;
  {
    auto context = CreateContext("dbid_uuid1", "license_id1");
    EXPECT_EQ(filter.Process(driver, context), cf::Result::kDisallow);
  }
  {
    auto context = CreateContext("dbid_uuid2", "");
    EXPECT_EQ(filter.Process(driver, context), cf::Result::kAllow);
  }
  {
    auto context = CreateContext("dbid_uuid3", "license_id3");
    EXPECT_EQ(filter.Process(driver, context), cf::Result::kAllow);
  }
}
