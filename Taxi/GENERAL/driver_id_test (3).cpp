#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_dbpark/fetch_dbpark_test.hpp>
#include <testing/taxi_config.hpp>
#include "driver_id.hpp"

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;

namespace {

candidates::Environment CreateEnvironment() {
  return candidates::Environment(dynamic_config::GetDefaultSnapshot());
}

}  // namespace

TEST(DriverIdFilter, NoParams) {
  formats::json::Value json;

  cf::infrastructure::DriverIdFactory factory;
  std::unique_ptr<cf::Filter> filter;
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  ASSERT_NO_THROW(filter = factory.Create(json, env));
  ASSERT_FALSE(filter);
}

TEST(DriverIdFilter, Sample) {
  formats::json::ValueBuilder excluded_ids(formats::json::Type::kArray);
  excluded_ids.PushBack("clid_uuid0");
  excluded_ids.PushBack("clid_uuid1");

  formats::json::ValueBuilder json(formats::json::Type::kObject);
  json["excluded_ids"] = std::move(excluded_ids);

  cf::infrastructure::DriverIdFactory factory;
  std::unique_ptr<cf::Filter> filter;
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  ASSERT_NO_THROW(filter = factory.Create(json.ExtractValue(), env));
  ASSERT_TRUE(filter);

  cf::Context context;
  cfi::test::SetClid(context, "clid");

  EXPECT_EQ(filter->Process({{}, "dbid_uuid0"}, context),
            cf::Result::kDisallow);
  EXPECT_EQ(filter->Process({{}, "dbid_uuid2"}, context), cf::Result::kAllow);
  EXPECT_EQ(filter->Process({{}, "dbid_uuid1"}, context),
            cf::Result::kDisallow);
}
