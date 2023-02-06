#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>
#include <userver/formats/json/serialize.hpp>

#include "requirements.hpp"

namespace {

models::Requirements MakeRequirements(const std::string& requirements,
                                      const dynamic_config::Snapshot& config) {
  return models::Requirements::Parse(formats::json::FromString(requirements),
                                     config);
}

}  // namespace

TEST(Requirements, Basic) {
  models::Requirements available({
      {"animaltransport", true},
      {"ski", true},
      {"yellowcarnumber", false},
      {"bicycle", short(1)},
  });

  EXPECT_EQ(true,
            available.IsSatisfy({{"animaltransport", true}, {"ski", true}}));
  EXPECT_EQ(true,
            available.IsSatisfy({{"animaltransport", false}, {"ski", true}}));
  EXPECT_EQ(true, available.IsSatisfy({{"bicycle", short(0)}, {"ski", true}}));
  EXPECT_EQ(true, available.IsSatisfy({{"bicycle", short(1)}, {"ski", true}}));

  EXPECT_EQ(false, available.IsSatisfy({{"bicycle", short(2)}, {"ski", true}}));
  EXPECT_EQ(false, available.IsSatisfy(
                       {{"bicycle", short(1)}, {"yellowcarnumber", true}}));
}

TEST(Requirements, Parser) {
  const auto config = dynamic_config::GetDefaultSnapshot();

  EXPECT_THROW(MakeRequirements("{\"bicycle\": \"lkv\"}", config),
               models::RequirementsError);
  EXPECT_NO_THROW(MakeRequirements("{\"bicycle\": true}", config));
}
