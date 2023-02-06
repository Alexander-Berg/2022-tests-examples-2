#include <userver/utest/utest.hpp>

#include <chrono>

#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>
#include "driver_metrics.hpp"

namespace cf = candidates::filters;
namespace cfe = cf::efficiency;
namespace cfi = cf::infrastructure;

const cf::FilterInfo kEmptyInfo;

static const auto kBlockingLag = std::chrono::seconds(5);

class DriverMetricsTest : public testing::Test {
 protected:
  void SetUp() override {
    // good
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license1", "license10"};
      unique_driver.driver_metrics_state = models::driver_metrics::State();
      unique_driver.driver_metrics_state->blocked = false;
      unique_drivers["uid1"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }

    // disallow
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license2", "license20"};
      unique_driver.driver_metrics_state = models::driver_metrics::State();
      unique_driver.driver_metrics_state->blocked = true;
      unique_drivers["uid2"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }
    // allow due to block is obsolete
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license2", "license20"};
      unique_driver.driver_metrics_state = models::driver_metrics::State();
      unique_driver.driver_metrics_state->blocked = true;
      unique_driver.driver_metrics_state->blocked_until =
          std::chrono::system_clock::now() - std::chrono::seconds(20);
      unique_drivers["uid3"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }
    // absent
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license4", "license40"};
      unique_drivers["uid4"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }
    // disallow due to block is still active
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license2", "license20"};
      unique_driver.driver_metrics_state = models::driver_metrics::State();
      unique_driver.driver_metrics_state->blocked = true;
      unique_driver.driver_metrics_state->blocked_until =
          std::chrono::system_clock::now() + std::chrono::seconds(20);
      unique_drivers["uid5"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }
    // disallowed due to block is in allowed blocking gap
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license2", "license20"};
      unique_driver.driver_metrics_state = models::driver_metrics::State();
      unique_driver.driver_metrics_state->blocked = true;
      unique_driver.driver_metrics_state->blocked_until =
          std::chrono::system_clock::now() - std::chrono::seconds(2);
      unique_drivers["uid6"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }
    // allow due to block is in allowed blocking gap
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license2", "license20"};
      unique_driver.driver_metrics_state = models::driver_metrics::State();
      unique_driver.driver_metrics_state->blocked = true;
      unique_driver.driver_metrics_state->blocked_until =
          std::chrono::system_clock::now() + std::chrono::seconds(2);
      unique_drivers["uid7"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }
  }

  cf::Context& GetContext(const std::string& uid) {
    context.ClearData();
    cfi::FetchUniqueDriver::Set(context, unique_drivers[uid]);
    return context;
  }

  std::unordered_map<std::string, models::UniqueDriverPtr> unique_drivers;
  cf::Context context;
};

TEST_F(DriverMetricsTest, Sample) {
  cfe::DriverMetrics filter(kEmptyInfo, kBlockingLag);
  ASSERT_EQ(cf::Result::kAllow, filter.Process({}, GetContext("uid1")));
  ASSERT_EQ(cf::Result::kAllow, filter.Process({}, GetContext("uid2")));
  ASSERT_EQ(cf::Result::kAllow, filter.Process({}, GetContext("uid3")));
  ASSERT_EQ(cf::Result::kAllow, filter.Process({}, GetContext("uid4")));
  ASSERT_EQ(cf::Result::kDisallow, filter.Process({}, GetContext("uid6")));
  ASSERT_EQ(cf::Result::kDisallow, filter.Process({}, GetContext("uid7")));
  ASSERT_EQ(cf::Result::kDisallow, filter.Process({}, GetContext("uid5")));
}
