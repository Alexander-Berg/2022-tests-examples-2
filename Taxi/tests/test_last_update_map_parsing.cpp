#include <gtest/gtest.h>

#include <models/localizations_cache_model.hpp>
#include <userver/formats/bson.hpp>
#include <utils/time_point.hpp>

TEST(TestLastUpdateMap, TestLastUpdateMapParsing) {
  auto bson_builder =
      formats::bson::ValueBuilder(formats::common::Type::kObject);

  bson_builder["keyset1"] = localizations_replica::utils::TimePoint();
  bson_builder["keyset2"] = localizations_replica::utils::TimePoint();
  bson_builder["keyset3"] = localizations_replica::utils::TimePoint();

  auto bson = bson_builder.ExtractValue();

  auto map = bson.As<localizations_replica::models::KeysetLastUpdateMap>();

  EXPECT_EQ(3, map.size());
}
