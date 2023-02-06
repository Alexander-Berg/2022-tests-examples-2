#include <userver/utest/utest.hpp>

#include <userver/engine/sleep.hpp>

#include "fetch_driver.hpp"

namespace {

namespace filters = candidates::filters;

models::DriverPtr DummyLoader(const std::string&) {
  engine::SleepFor(std::chrono::milliseconds(50));
  return {};
}

const filters::FilterInfo kEmptyInfo;

}  // namespace

UTEST_MT(FetchDriver, One, 2) {
  auto drivers = std::make_shared<models::Drivers>(&DummyLoader);
  drivers->Insert("dbid_uuid", std::make_shared<models::Driver>());

  filters::infrastructure::FetchDriver filter(kEmptyInfo, drivers);
  {
    filters::Context context;
    candidates::GeoMember member{{}, "dbid_uuid"};

    EXPECT_EQ(filters::Result::kAllow, filter.Process(member, context));
    EXPECT_NO_THROW(filters::infrastructure::FetchDriver::Get(context));
  }
  {
    filters::Context context;
    candidates::GeoMember member{{}, "not_found"};

    EXPECT_EQ(filters::Result::kRepeat, filter.Process(member, context));
    EXPECT_ANY_THROW(filters::infrastructure::FetchDriver::Get(context));
  }
}
