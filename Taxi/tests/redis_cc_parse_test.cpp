#include <userver/utest/utest.hpp>

#include <userver/formats/json/value_builder.hpp>
#include <userver/storages/redis/redis_config.hpp>

namespace {
::redis::CommandControl::Strategy DoParse(const std::string& str) {
  return Parse(formats::json::ValueBuilder(str).ExtractValue(),
               formats::parse::To<::redis::CommandControl::Strategy>());
}
}  // namespace

TEST(RedisCommandControlStrategy, FromString) {
  using redis::CommandControl;
  EXPECT_EQ(DoParse("local_dc_conductor"),
            CommandControl::Strategy::kLocalDcConductor);
  EXPECT_EQ(DoParse("every_dc"), CommandControl::Strategy::kEveryDc);
  EXPECT_EQ(DoParse("nearest_server_ping"),
            CommandControl::Strategy::kNearestServerPing);
  EXPECT_EQ(DoParse("default"), CommandControl::Strategy::kDefault);
  EXPECT_EQ(DoParse("invalid"), CommandControl::Strategy::kEveryDc);
}
