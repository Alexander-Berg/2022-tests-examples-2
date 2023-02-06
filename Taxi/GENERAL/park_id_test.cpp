#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_dbpark/fetch_dbpark_test.hpp>
#include <testing/taxi_config.hpp>
#include "park_id.hpp"

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;

namespace {

const cf::FilterInfo kEmptyInfo;

candidates::Environment CreateEnvironment() {
  return candidates::Environment(dynamic_config::GetDefaultSnapshot());
}

}  // namespace

TEST(ParkIdFilter, NoParams) {
  formats::json::Value json;

  cf::infrastructure::ParkIdFactory factory;
  std::unique_ptr<cf::Filter> filter;
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  ASSERT_NO_THROW(filter = factory.Create(json, env));
  ASSERT_FALSE(filter);
}

TEST(ParkIdFilter, Sample) {
  formats::json::ValueBuilder excluded_ids(formats::json::Type::kArray);
  excluded_ids.PushBack("clid0");
  excluded_ids.PushBack("clid1");

  formats::json::ValueBuilder json(formats::json::Type::kObject);
  json["excluded_park_ids"] = std::move(excluded_ids);

  cf::infrastructure::ParkIdFactory factory;
  std::unique_ptr<cf::Filter> filter;
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  ASSERT_NO_THROW(filter = factory.Create(json.ExtractValue(), env));
  ASSERT_TRUE(filter);

  cf::Context context;
  cfi::test::SetClid(context, "clid0");
  EXPECT_EQ(filter->Process({}, context), cf::Result::kDisallow);
  cfi::test::SetClid(context, "clid2");
  EXPECT_EQ(filter->Process({}, context), cf::Result::kAllow);
  cfi::test::SetClid(context, "clid1");
  EXPECT_EQ(filter->Process({}, context), cf::Result::kDisallow);
}
