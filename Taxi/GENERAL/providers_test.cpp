#include <gtest/gtest.h>

#include <models/provider/provider.hpp>

TEST(TestProviders, ProviderTypeCountEqualToAllEnumTypes) {
  const auto real_provider_count = []() constexpr->int32_t {
    int32_t count = 0;
    for (int32_t i = 0; i < models::kProviderTypeCount + 1; ++i) {
      switch (static_cast<models::ProviderType>(i)) {
        case models::ProviderType::kManual:
        case models::ProviderType::kService:
        case models::ProviderType::kYql:
          ++count;
      }
    }
    return count;
  };

  static_assert(real_provider_count() == models::kProviderTypeCount);

  ASSERT_EQ(real_provider_count(), models::kProviderTypeCount);
}
