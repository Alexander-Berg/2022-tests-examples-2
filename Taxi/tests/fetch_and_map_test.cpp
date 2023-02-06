#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <vector>

#include <userver/cache/statistics_mock.hpp>

#include <clients/taxi-tariffs/client.hpp>
#include <clients/taxi-tariffs/client_gmock.hpp>

#include <utils/utils.hpp>

namespace tt = clients::taxi_tariffs;

struct FetchAndMapTestData {
  const tt::v1_tariffs::get::Response tt_response;
  const subvention_dependencies::models::TariffsMap expected;
};

struct FetchAndMapTestParametrized
    : public ::testing::TestWithParam<FetchAndMapTestData> {};

TEST_P(FetchAndMapTestParametrized, FetchAndMapTestParametrized) {
  const auto [tt_response, expected] = GetParam();

  tt::ClientGMock tt_mock;
  EXPECT_CALL(tt_mock, getTariffs(testing::_, testing::_))
      .Times(1)
      .WillOnce(testing::Return(tt_response));

  cache::UpdateStatisticsScopeMock stats(cache::UpdateType::kFull);

  auto response = subvention_dependencies::utils::FetchTariffsAndMakeMap(
      tt_mock, stats.GetScope());

  ASSERT_EQ(response, expected);
}

const std::vector<FetchAndMapTestData> kFetchAndMapTestData = {
    {tt::v1_tariffs::get::Response(tt::GetTariffsResponse{
         {tt::TariffsItem{
              "id1", "hz1", "az1", {"rz11", "rz12"}, {"cn1", "cn2", "cn3"}},
          tt::TariffsItem{"id2", "hz2", "az2", {"rz21"}, {}}}}),
     subvention_dependencies::models::TariffsMap(
         {{"hz1",
           {"id1", "hz1", "az1", {"rz11", "rz12"}, {"cn1", "cn2", "cn3"}}},
          {"hz2", {"id2", "hz2", "az2", {"rz21"}, {}}}})}};

INSTANTIATE_TEST_SUITE_P(FetchAndMapTestParametrized,
                         FetchAndMapTestParametrized,
                         ::testing::ValuesIn(kFetchAndMapTestData));
