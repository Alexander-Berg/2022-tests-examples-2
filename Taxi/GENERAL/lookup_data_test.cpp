#include <gtest/gtest.h>

#include "lookup_data.hpp"

using lookup::models::statistics::LookupData;

TEST(LookupData, ClassIndexesTest) {
  const std::string kUnknown = "unknown";

  for (size_t idx = 0; idx < LookupData::kClassesSize; ++idx) {
    const auto id = static_cast<LookupData::Ids>(idx);
    EXPECT_NE(LookupData::GetClassName(id), kUnknown);
  }
}
