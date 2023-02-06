#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_dbpark/fetch_dbpark.hpp>
#include <filters/partners/park_providers/park_providers.hpp>
#include <models/providers.hpp>
#include <mongo/names/dbparks.hpp>

namespace {

namespace providers = candidates::mongo::names::dbparks::providers;
namespace cf = candidates::filters;
const cf::FilterInfo kEmptyInfo;

struct TestCase {
  std::vector<std::string> providers;
  cf::Result expected_result;
};

class ParkProvidersTestCase : public ::testing::TestWithParam<TestCase> {};
}  // namespace

UTEST_P(ParkProvidersTestCase, Filter) {
  const auto& param = GetParam();

  cf::partners::ParkProviders filter(kEmptyInfo);

  cf::Context context{};
  auto park = std::make_shared<models::DbPark>(
      models::DbPark{"dbid0", "clid0", "moscow",
                     models::providers::ProviderMask(param.providers)});
  cf::infrastructure::FetchDbPark::Set(context, park);

  candidates::GeoMember member{{}, "dbid0_uuid0"};

  EXPECT_EQ(filter.Process(member, context), param.expected_result);
}

INSTANTIATE_UTEST_SUITE_P(
    ParkProvidersTests, ParkProvidersTestCase,
    ::testing::Values(TestCase{{providers::kYandex}, cf::Result::kAllow},
                      TestCase{{""}, cf::Result::kDisallow}));
