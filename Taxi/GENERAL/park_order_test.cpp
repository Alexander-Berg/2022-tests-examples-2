#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>
#include "park_order.hpp"

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;

namespace {

candidates::Environment CreateEnvironment() {
  return candidates::Environment(dynamic_config::GetDefaultSnapshot());
}

}  // namespace

TEST(ParkOrderFilter, NoParams) {
  formats::json::Value json;

  cf::infrastructure::ParkOrderFactory factory;
  std::unique_ptr<cf::Filter> filter;
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  ASSERT_NO_THROW(filter = factory.Create(json, env));
  ASSERT_FALSE(filter);

  json = formats::json::FromString(R"=({"order": {}})=");
  ASSERT_NO_THROW(filter = factory.Create(json, env));
  ASSERT_FALSE(filter);
}

TEST(ParkOrderFilter, ExclusiveOrder) {
  formats::json::Value json = formats::json::FromString(R"=(
  {
    "order": {
      "request": {
        "white_label_requirements": {
          "source_park_id": "dbid0",
          "dispatch_requirement": "only_source_park"
        }
      }
    }
  }
  )=");

  cf::infrastructure::ParkOrderFactory factory;
  std::unique_ptr<cf::Filter> filter;
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  ASSERT_NO_THROW(filter = factory.Create(json, env));
  ASSERT_TRUE(filter);

  cf::Context context;
  EXPECT_EQ(filter->Process({{}, "dbid0_uuid0"}, context), cf::Result::kAllow);
  EXPECT_EQ(filter->Process({{}, "dbid1_uuid1"}, context),
            cf::Result::kDisallow);
}

TEST(ParkOrderFilter, MixedOrder) {
  formats::json::Value json = formats::json::FromString(R"=(
  {
    "order": {
      "request": {
        "white_label_requirements": {
          "source_park_id": "dbid0",
          "dispatch_requirement": "source_park_and_all"
        }
      }
    }
  }
  )=");

  cf::infrastructure::ParkOrderFactory factory;
  std::unique_ptr<cf::Filter> filter;
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  ASSERT_NO_THROW(filter = factory.Create(json, env));
  ASSERT_FALSE(filter);
}
