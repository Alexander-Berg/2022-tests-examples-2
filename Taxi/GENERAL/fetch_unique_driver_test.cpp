#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <userver/utest/utest.hpp>
#include "fetch_unique_driver.hpp"

namespace {

namespace cf = candidates::filters;
namespace cfi = candidates::filters::infrastructure;

const cf::FilterInfo kEmptyInfo;

void AddToContext(models::Driver&& driver, cf::Context& context) {
  cfi::FetchDriver::Set(
      context, std::make_shared<const models::Driver>(std::move(driver)));
}

models::UniqueDriverPtr DummyLoader(const std::string&) { return {}; }

}  // namespace

UTEST(FetchUniqueDriver, NoDriver) {
  auto drivers = std::make_shared<models::UniqueDrivers>(&DummyLoader);
  cfi::FetchUniqueDriver filter(kEmptyInfo, drivers);
  candidates::GeoMember member;
  cf::Context context;
  EXPECT_ANY_THROW(filter.Process(member, context));
}

UTEST(FetchUniqueDriver, Sample) {
  auto drivers = std::make_shared<models::UniqueDrivers>(&DummyLoader);
  drivers->Insert("lic1", std::make_shared<models::UniqueDriver>());

  cfi::FetchUniqueDriver filter(kEmptyInfo, drivers);
  candidates::GeoMember member;
  {
    cf::Context context;
    models::Driver driver;
    driver.license_id = "lic1";
    AddToContext(std::move(driver), context);

    EXPECT_EQ(cf::Result::kAllow, filter.Process(member, context));
    EXPECT_NO_THROW(cfi::FetchUniqueDriver::Get(context));
  }
  {
    cf::Context context;
    models::Driver driver;
    driver.license_id = "lic2";
    AddToContext(std::move(driver), context);

    EXPECT_EQ(cf::Result::kRepeat, filter.Process(member, context));
    EXPECT_ANY_THROW(cfi::FetchUniqueDriver::Get(context));
  }
}
