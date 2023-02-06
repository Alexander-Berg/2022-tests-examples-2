#include <gtest/gtest.h>

#include <string>
#include <unordered_map>
#include <vector>

#include <clients/eats-discounts/client.hpp>
#include <clients/eats-discounts/definitions.hpp>

#include <requesters/discounts.hpp>
#include <requesters/utils.hpp>
#include <tests/utils.hpp>
#include <userver/logging/log.hpp>

namespace eats_discounts_applicator::requesters::tests {

namespace {

using namespace eats_discounts_applicator::tests;
using HierarchyName = clients::eats_discounts::HierarchyName;

clients::eats_discounts::FetchedMenuDiscounts MakeFetchedMenuDiscounts(
    DiscountType type, const std::vector<std::string>& products_ids,
    bool is_excluded = false,
    const std::optional<std::string>& promotype = std::nullopt) {
  return {1,
          {discounts_client::FetchedMenuDiscountsDiscountsA{
              MakeV2MenuDiscount(type, "10", std::nullopt, promotype),
              {products_ids, is_excluded}}}};
}

clients::eats_discounts::FetchedCashbacks MakeFetchedCashback(
    CashbackType type, const std::vector<std::string>& products_ids,
    bool is_excluded = false) {
  const auto cashback = MakeMatchedCashback(type);
  if (!cashback) {
    return {};
  }
  return {1,
          {discounts_client::FetchedCashbacksDiscountsA{
              cashback.value(), {products_ids, is_excluded}}}};
}

void AddFetchedMenuDiscount(
    clients::eats_discounts::FetchedMenuDiscounts& discounts, DiscountType type,
    const std::vector<std::string>& products_ids, bool is_excluded = false,
    const std::optional<std::string>& promotype = std::nullopt) {
  discounts.total_count++;
  discounts.discounts.push_back(
      discounts_client::FetchedMenuDiscountsDiscountsA{
          MakeV2MenuDiscount(type, "10", std::nullopt, promotype),
          {products_ids, is_excluded}});
}

StatsInfo MakeStatsInfo() { return {10, {}, {}, {}, {}, {}}; }

}  // namespace

namespace discounts {

TEST(TestParseDiscounts, NoResponses) {
  std::vector<discounts_fetch::Response200> responses;
  const auto discounts =
      ParseDiscounts(responses, kEmptyExcludedInformation, kPromoTypesInfo);
  ASSERT_EQ(discounts.size(), 0);
}

TEST(TestParseDiscounts, ExcludedNotSupported) {
  discounts_fetch::Response200 response;
  response.menu_discounts =
      MakeFetchedMenuDiscounts(DiscountType::AbsoluteValue, {"1"}, true);
  const auto discounts =
      ParseDiscounts({response}, kEmptyExcludedInformation, kPromoTypesInfo);
  ASSERT_EQ(discounts.size(), 0);
}

TEST(TestParseDiscounts, OneDiscountTwoProducts) {
  discounts_fetch::Response200 response;
  response.menu_discounts =
      MakeFetchedMenuDiscounts(DiscountType::AbsoluteValue, {"1", "2"});
  const auto discounts =
      ParseDiscounts({response}, kEmptyExcludedInformation, kPromoTypesInfo);
  ASSERT_EQ(discounts.size(), 2);
  ASSERT_EQ(discounts.count("1"), 1);
  ASSERT_EQ(discounts.count("2"), 1);
}

TEST(TestParseDiscounts, TwoDiscountsOneProduct) {
  const std::string id = "1";
  discounts_fetch::Response200 response;
  response.menu_discounts =
      MakeFetchedMenuDiscounts(DiscountType::AbsoluteValue, {id});
  AddFetchedMenuDiscount(response.menu_discounts.value(),
                         DiscountType::FractionWithMaximum, {id});
  const auto discounts =
      ParseDiscounts({response}, kEmptyExcludedInformation, kPromoTypesInfo);
  ASSERT_EQ(discounts.size(), 1);
  ASSERT_EQ(discounts.at(id).size(), 2);
}

TEST(TestParseDiscounts, ExcludeDiscountsByPromotype) {
  discounts_fetch::Response200 response;
  response.menu_discounts = MakeFetchedMenuDiscounts(
      DiscountType::AbsoluteValue, {"1", "2"}, false, "cucumber");
  const auto discounts = ParseDiscounts(
      {response}, experiments::ExcludedInformation{{"one", "cucumber"}, {}},
      {{"cucumber", {"name", "descr", "pict"}}});
  ASSERT_EQ(discounts.size(), 0);
}

TEST(TestParseDiscounts, ExcludeDiscountsByType) {
  discounts_fetch::Response200 response;
  response.menu_discounts =
      MakeFetchedMenuDiscounts(DiscountType::AbsoluteValue, {"1", "2"});
  const auto discounts = ParseDiscounts(
      {response},
      experiments::ExcludedInformation{
          {},
          {ExpDiscountType::kYandexMenuMoneyDiscount} /*exluded_discounts*/},
      kPromoTypesInfo);
  ASSERT_EQ(discounts.size(), 0);
}

TEST(TestParseDiscounts, NoMenuDiscount) {
  const std::string id = "1";
  std::vector<discounts_fetch::Response200> responses;
  responses.push_back({/*menu_discounts*/ std::nullopt,
                       MakeFetchedCashback(CashbackType::AbsoluteValue, {id}),
                       /*yandex_menu_cashback*/ std::nullopt,
                       /*retail_menu_discounts*/ std::nullopt,
                       /*restaurant_menu_discounts*/ std::nullopt});
  responses.push_back({/*menu_discounts*/ std::nullopt,
                       /*place_menu_cashback*/ std::nullopt,
                       MakeFetchedCashback(CashbackType::AbsoluteValue, {id}),
                       /*retail_menu_discounts*/ std::nullopt,
                       /*restaurant_menu_discounts*/ std::nullopt});

  const auto discounts =
      ParseDiscounts(responses, kEmptyExcludedInformation, kPromoTypesInfo);
  ASSERT_EQ(discounts.size(), 0);
}

}  // namespace discounts

namespace cashback {

TEST(TestParseCashback, NoResponses) {
  std::vector<discounts_fetch::Response200> responses;
  const auto cashbacks = ParseCashbacks(responses);
  ASSERT_EQ(cashbacks.size(), 0);
}

TEST(TestParseCashback, PlaceExcludedNotSupported) {
  discounts_fetch::Response200 response;
  response.place_menu_cashback =
      MakeFetchedCashback(CashbackType::AbsoluteValue, {"1"}, true);
  const auto cashbacks = ParseCashbacks({response});
  ASSERT_EQ(cashbacks.size(), 0);
}

TEST(TestParseCashback, YandexExcludedNotSupported) {
  discounts_fetch::Response200 response;
  response.yandex_menu_cashback =
      MakeFetchedCashback(CashbackType::AbsoluteValue, {"1"}, true);
  const auto cashbacks = ParseCashbacks({response});
  ASSERT_EQ(cashbacks.size(), 0);
}

TEST(TestParseCashback, OneCashbackOnProducts) {
  discounts_fetch::Response200 response;
  response.place_menu_cashback =
      MakeFetchedCashback(CashbackType::AbsoluteValue, {"1", "2"});
  response.yandex_menu_cashback =
      MakeFetchedCashback(CashbackType::AbsoluteValue, {"3", "4"});
  const auto cashbacks = ParseCashbacks({response});
  ASSERT_EQ(cashbacks.size(), 4);
  ASSERT_EQ(cashbacks.count("1"), 1);
  ASSERT_EQ(cashbacks.count("2"), 1);
  ASSERT_EQ(cashbacks.count("3"), 1);
  ASSERT_EQ(cashbacks.count("4"), 1);
}

TEST(TestParseCashback, TwoCashbacksOnProduct) {
  const std::string id = "1";
  discounts_fetch::Response200 response;
  response.place_menu_cashback =
      MakeFetchedCashback(CashbackType::AbsoluteValue, {id});
  response.yandex_menu_cashback =
      MakeFetchedCashback(CashbackType::AbsoluteValue, {id});
  const auto cashbacks = ParseCashbacks({response});
  ASSERT_EQ(cashbacks.size(), 1);
  ASSERT_EQ(cashbacks.at(id).size(), 2);
}

TEST(TestParseCashback, NoCashback) {
  discounts_fetch::Response200 response;
  response.menu_discounts =
      MakeFetchedMenuDiscounts(DiscountType::AbsoluteValue, {"1"}, true);
  const auto cashbacks = ParseCashbacks({response});
  ASSERT_EQ(cashbacks.size(), 0);
}

}  // namespace cashback

namespace fetch_request {

template <class Parameters>
void AssertParameters(Parameters parameters, size_t batch_size, size_t offset) {
  ASSERT_EQ(parameters.has_value(), true);
  ASSERT_EQ(parameters.value().cursor.limit, batch_size);
  ASSERT_EQ(parameters.value().cursor.offset, offset);
}

TEST(TestMakeV2FetchRequest, BasicTest) {
  std::vector<size_t> batch_sizes = {1, 5, 10, 100};
  std::vector<std::unordered_set<HierarchyName>> hierarchies = {
      {HierarchyName::kMenuDiscounts},
      {HierarchyName::kYandexMenuCashback, HierarchyName::kPlaceMenuCashback},
      {HierarchyName::kYandexMenuCashback, HierarchyName::kPlaceMenuCashback,
       HierarchyName::kMenuDiscounts},
      {}};
  std::vector<size_t> offsets = {0, 100, 2000};
  std::chrono::system_clock::time_point delivery_time = utils::datetime::Now();

  for (const auto& batch_size : batch_sizes) {
    for (const auto& hierarchies_set : hierarchies) {
      for (const auto& offset : offsets) {
        const auto request = MakeV2FetchRequest(
            {}, hierarchies_set, batch_size, offset, MakeStatsInfo(),
            {"tag1", "tag2"}, {"one", "two"}, delivery_time);
        const auto& fetch_parameters =
            request.body.hierarchies_fetch_parameters;
        if (hierarchies_set.count(HierarchyName::kMenuDiscounts) != 0) {
          AssertParameters(fetch_parameters.menu_discounts, batch_size, offset);
        }
        if (hierarchies_set.count(HierarchyName::kPlaceMenuCashback) != 0) {
          AssertParameters(fetch_parameters.place_menu_cashback, batch_size,
                           offset);
        }
        if (hierarchies_set.count(HierarchyName::kYandexMenuCashback) != 0) {
          AssertParameters(fetch_parameters.yandex_menu_cashback, batch_size,
                           offset);
        }
      }
    }
  }
}

}  // namespace fetch_request

namespace fetch_requests {

struct ResponseParam {
  HierarchyName hierarchy;
  size_t total_count;
  size_t fetched_size;
};

template <class Discount>
std::vector<Discount> MakeMenuDiscounts(size_t discounts_size) {
  std::vector<Discount> discounts;
  for (size_t i = 0; i < discounts_size; i++) {
    discounts.push_back({});
  }
  return discounts;
}

discounts_fetch::Response200 MakeResponse(
    const std::vector<ResponseParam>& params) {
  discounts_fetch::Response200 response;
  for (const auto& param : params) {
    switch (param.hierarchy) {
      case HierarchyName::kMenuDiscounts:
        response.menu_discounts = discounts_client::FetchedMenuDiscounts{
            param.total_count,
            MakeMenuDiscounts<discounts_client::FetchedMenuDiscountsDiscountsA>(
                param.fetched_size)};
        break;
      case HierarchyName::kYandexMenuCashback:
        response.yandex_menu_cashback = discounts_client::FetchedCashbacks{
            param.total_count,
            MakeMenuDiscounts<discounts_client::FetchedCashbacksDiscountsA>(
                param.fetched_size)};
        break;
      case HierarchyName::kPlaceMenuCashback:
        response.place_menu_cashback = discounts_client::FetchedCashbacks{
            param.total_count,
            MakeMenuDiscounts<discounts_client::FetchedCashbacksDiscountsA>(
                param.fetched_size)};
        break;
      default:
        break;
    }
  }
  return response;
}

struct TestParams {
  size_t total_count;
  size_t fetched_size;
  size_t batch_size;
  std::vector<discounts_client::RandomAccessCursor> expected_cursors;
  std::string test_name;
};

class TestMakeV2FetchRequests : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TestParams> kBasicTestParams = {
    {0, 0, 0, {}, "empty_response"},
    {500, 500, 500, {}, "all_fetched"},
    {1000, 500, 500, {{500, 500}}, "one_fetch"},
    {2000, 500, 600, {{600, 500}, {600, 1100}, {300, 1700}}, "few_fetchs"},
};

TEST_P(TestMakeV2FetchRequests, MenuDiscounts) {
  const auto hierarchies = {HierarchyName::kPlaceMenuCashback,
                            HierarchyName::kYandexMenuCashback,
                            HierarchyName::kMenuDiscounts};
  const auto& params = GetParam();
  std::chrono::system_clock::time_point delivery_time = utils::datetime::Now();
  for (const auto& hierarchy : hierarchies) {
    const auto requests = MakeV2FetchRequests(
        {},
        MakeResponse({{hierarchy, params.total_count, params.fetched_size}}),
        params.batch_size, MakeStatsInfo(), {"tag1", "tag2"}, {"one", "two"},
        delivery_time);
    ASSERT_EQ(requests.size(), params.expected_cursors.size());
    for (size_t i = 0; i < requests.size(); i++) {
      switch (hierarchy) {
        case HierarchyName::kMenuDiscounts:
          ASSERT_EQ(
              requests[i]
                  .body.hierarchies_fetch_parameters.menu_discounts.value()
                  .cursor,
              params.expected_cursors[i]);
          break;
        case HierarchyName::kYandexMenuCashback:
          ASSERT_EQ(requests[i]
                        .body.hierarchies_fetch_parameters.yandex_menu_cashback
                        .value()
                        .cursor,
                    params.expected_cursors[i]);
          break;
        case HierarchyName::kPlaceMenuCashback:
          ASSERT_EQ(
              requests[i]
                  .body.hierarchies_fetch_parameters.place_menu_cashback.value()
                  .cursor,
              params.expected_cursors[i]);
          break;
        default:
          throw std::runtime_error("Hierarchy not supported");
      }
    }
  }
}

TEST(MakeV2FetchRequests, DiscountWithCashback) {
  std::chrono::system_clock::time_point delivery_time = utils::datetime::Now();
  const auto requests = MakeV2FetchRequests(
      {},
      MakeResponse({{HierarchyName::kMenuDiscounts, 1000, 500},
                    {HierarchyName::kYandexMenuCashback, 800, 500},
                    {HierarchyName::kPlaceMenuCashback, 1600, 500}}),
      500, MakeStatsInfo(), {"tag1", "tag2", "tag3"}, {"one", "two"},
      delivery_time);
  ASSERT_EQ(requests.size(), 5);
  size_t menu_discounts_requests = 0;
  size_t place_cashback_requests = 0;
  size_t yandex_cashback_requests = 0;
  for (const auto& request : requests) {
    const auto& result = request.body.hierarchies_fetch_parameters;
    if (result.menu_discounts.has_value()) {
      menu_discounts_requests++;
    }
    if (result.place_menu_cashback.has_value()) {
      place_cashback_requests++;
    }
    if (result.yandex_menu_cashback.has_value()) {
      yandex_cashback_requests++;
    }
  }
  ASSERT_EQ(menu_discounts_requests, 1);
  ASSERT_EQ(yandex_cashback_requests, 1);
  ASSERT_EQ(place_cashback_requests, 3);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestMakeV2FetchRequests,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace fetch_requests

}  // namespace eats_discounts_applicator::requesters::tests
