#include <userver/utest/utest.hpp>

#include <chrono>

#include <userver/formats/bson/inline.hpp>
#include <userver/formats/bson/value_builder.hpp>
#include <userver/utest/parameter_names.hpp>
#include <userver/utils/datetime.hpp>

#include <geometry/position.hpp>
#include <geometry/serialization/position.hpp>
#include <testing/taxi_config.hpp>

#include <core/models/offers.hpp>
#include <core/offers_match.hpp>
#include <taxi_config/variables/ORDER_OFFERS_PAYMENT_TYPES_REQUIREMENTS.hpp>
#include <utils/bson.hpp>

namespace order_offers::core {

namespace fb = formats::bson;

using namespace std::chrono_literals;

using TimePoint = std::chrono::system_clock::time_point;

namespace {

models::RequirementsDescriptions BuildDefaultRequirementsDescriptions() {
  models::RequirementsDescription ski;
  ski.name = "ski";

  models::RequirementsDescription yellowcarnumber;
  yellowcarnumber.name = "yellowcarnumber";
  yellowcarnumber.tariff_specific = false;

  models::RequirementsDescription door_to_door;
  door_to_door.name = "door_to_door";
  door_to_door.tariff_specific = true;

  models::RequirementsDescription childchair_v2;
  childchair_v2.name = "childchair_v2";
  childchair_v2.tariff_specific = true;

  return {
      {"ski", ski},
      {"yellowcarnumber", yellowcarnumber},
      {"door_to_door", door_to_door},
      {"childchair_v2", childchair_v2},
  };
}

OfferMatcher GetDefaultOfferMatcher() {
  const auto configs = dynamic_config::GetDefaultSnapshot();
  static const auto payment_types_requirements =
      configs[taxi_config::ORDER_OFFERS_PAYMENT_TYPES_REQUIREMENTS];

  static const auto requirements_descriptions =
      BuildDefaultRequirementsDescriptions();

  const int offer_ttl_seconds = 600;
  return OfferMatcher({offer_ttl_seconds, payment_types_requirements},
                      requirements_descriptions);
}

const std::string kOfferId = "18d3a1133568d1c0fa5436123afbc370";
const std::string kOtherOfferId = "18d3a1133568d1c0fa5436123afbc371";

const auto kOfferDueTime = ::utils::datetime::GuessStringtime(
    "2022-02-08T10:47:55.724376343+03:00", "Europe/Moscow");
const auto kOrderDueTime = kOfferDueTime + 5min;

using geometry::lat;
using geometry::lon;

const models::Route kDefaultRoute = {
    {37.642971 * lon, 55.734989 * lat},
    {37.534576 * lon, 55.750573 * lat},
};

models::OfferDoc GetDefaultOffer(const models::TariffClasses& classes = {}) {
  auto prices = fb::ValueBuilder(formats::common::Type::kArray);
  for (const auto& class_ : classes) {
    prices.PushBack(fb::MakeDoc("cls", class_));
  }

  return fb::MakeDoc("_id", kOfferId,                                       //
                     "due", kOfferDueTime,                                  //
                     "route", utils::bson::ArrayFromVector(kDefaultRoute),  //
                     "prices", prices.ExtractValue()                        //
  );
}

models::MatchFilters GetDefaultMatchFilters() {
  const auto order = fb::MakeDoc("due", kOrderDueTime,  //
                                 "route",
                                 utils::bson::ArrayFromVector(kDefaultRoute)  //
  );
  return fb::MakeDoc("order", order);
}

}  // namespace

struct OfferDueTestParams {
  TimePoint order_due_time;
  bool offer_matches;

  std::string test_name;
};

class OfferDueTest : public testing::TestWithParam<OfferDueTestParams> {};

const std::vector<OfferDueTestParams> kOfferDueTestValues = {
    {kOfferDueTime + 5min, true, "OrderAfter_NotExpired"},
    {kOfferDueTime + 15min, false, "OrderAfter_Expired"},
    {kOfferDueTime - 5min, true, "OrderBefore_NotExpired"},
    {kOfferDueTime - 15min, false, "OrderBefore_Expired"},
};

TEST_P(OfferDueTest, Basic) {
  const auto& params = GetParam();

  const auto offer = GetDefaultOffer();

  auto filters = fb::ValueBuilder(GetDefaultMatchFilters());
  filters["order"]["due"] = params.order_due_time;

  const auto offer_matcher = GetDefaultOfferMatcher();

  EXPECT_EQ(offer_matcher.OfferMatchesFilters(offer, filters.ExtractValue()),
            params.offer_matches);
}

INSTANTIATE_TEST_SUITE_P(OffersMatch, OfferDueTest,
                         testing::ValuesIn(kOfferDueTestValues),
                         ::utest::PrintTestName());

struct OfferRouteTestParams {
  models::Route offer_route;
  models::Route order_route;

  bool offer_matches;

  std::string test_name;
};

class OfferRouteTest : public testing::TestWithParam<OfferRouteTestParams> {};

const auto kEmptyRoute = models::Route{};
const auto kReversedDefaultRoute =
    models::Route(kDefaultRoute.rbegin(), kDefaultRoute.rend());

const auto kExtendedRoute = models::Route{
    kDefaultRoute[0], kDefaultRoute[1], {37.589321 * lon, 55.734221 * lat}};
const auto kReversedExtendedRoute =
    models::Route(kExtendedRoute.rbegin(), kExtendedRoute.rend());

const std::vector<OfferRouteTestParams> kOfferRouteTestValues = {
    {
        kEmptyRoute,
        kEmptyRoute,
        true,
        "EmptyRoute_Matched",
    },
    {
        {kDefaultRoute[0]},
        {kDefaultRoute[0]},
        true,
        "SinglePointRoute_Matched",
    },
    {
        {kDefaultRoute[0]},
        {kDefaultRoute[1]},
        false,
        "SinglePointRoute_NotMatched",
    },
    {
        {{37.642971 * lon, 55.734989 * lat}},
        {{37.642871 * lon, 55.734789 * lat}},
        true,
        "SinglePoint_SmallOffset_Matched",
    },
    {
        {{37.642971 * lon, 55.734989 * lat}},
        {{37.642971 * lon, 55.734589 * lat}},
        false,
        "SinglePoint_BigOffset_NotMatched",
    },
    {
        kDefaultRoute,
        kDefaultRoute,
        true,
        "TwoPointRoute_Matched",
    },
    {
        kDefaultRoute,
        kReversedDefaultRoute,
        false,
        "TwoPointRouteReversed_NotMatched",
    },
    {
        kDefaultRoute,
        kExtendedRoute,
        false,
        "DifferentRouteSizes_NotMatched",
    },
    {
        kExtendedRoute,
        kExtendedRoute,
        true,
        "ThreePointRoute_Matched",
    },
    {
        kExtendedRoute,
        kReversedExtendedRoute,
        false,
        "ThreePointRouteReversed_NotMatched",
    },
};

TEST_P(OfferRouteTest, Basic) {
  const auto& params = GetParam();

  auto offer = fb::ValueBuilder(GetDefaultOffer());
  offer["route"] = utils::bson::ArrayFromVector(params.offer_route);

  auto filters = fb::ValueBuilder(GetDefaultMatchFilters());
  filters["order"]["route"] = utils::bson::ArrayFromVector(params.order_route);

  const auto offer_matcher = GetDefaultOfferMatcher();

  EXPECT_EQ(offer_matcher.OfferMatchesFilters(offer.ExtractValue(),
                                              filters.ExtractValue()),
            params.offer_matches);
}

INSTANTIATE_TEST_SUITE_P(OffersMatch, OfferRouteTest,
                         testing::ValuesIn(kOfferRouteTestValues),
                         ::utest::PrintTestName());

struct PaidSupplyTestParams {
  models::TariffClasses offer_paid_supply_classes;
  models::TariffClasses order_classes;
  std::optional<std::string> order_offer_id;

  bool offer_matches;

  std::string test_name;
};

class PaidSupplyTest : public testing::TestWithParam<PaidSupplyTestParams> {};

const std::vector<PaidSupplyTestParams> kPaidSupplyTestValues = {
    {
        {},
        {},
        {},
        true,
        "NoOfferPaidClasses_NoOrderClasses_NoOrderOfferId_Matched",
    },
    {
        {},
        {},
        kOfferId,
        true,
        "NoOfferPaidClasses_NoOrderClasses_OrderOfferId_Matched",
    },
    {
        {},
        {"econom", "comfort", "business"},
        {},
        true,
        "NoOfferPaidClasses_OrderClasses_NoOrderOfferId_Matched",
    },
    {
        {},
        {"econom", "comfort", "business"},
        kOfferId,
        true,
        "NoOfferPaidClasses_OrderClasses_OrderOfferId_Matched",
    },
    {
        {"econom", "comfort", "business"},
        {},
        {},
        true,
        "OfferPaidClasses_NoOrderClasses_NoOrderOfferId_Matched",
    },
    {
        {"econom", "comfort", "business"},
        {},
        kOfferId,
        true,
        "OfferPaidClasses_NoOrderClasses_OrderOfferId_Matched",
    },
    {
        {"econom", "comfort", "business"},
        {"ultima", "vip"},
        {},
        true,
        "NoCommonClasses_NoOrderOfferId_Matched",
    },
    {
        {"econom", "comfort", "business"},
        {"ultima", "vip"},
        kOfferId,
        true,
        "NoCommonClasses_OrderOfferId_Matched",
    },
    {
        {"econom", "comfort", "business"},
        {"business", "vip"},
        {},
        false,
        "CommonClassesIntersect_NoOrderOfferId_NotMatched",
    },
    {
        {"econom", "comfort", "business"},
        {"business", "vip"},
        kOtherOfferId,
        false,
        "CommonClassesIntersect_OrderOtherOfferId_Matched",
    },
    {
        {"econom", "comfort", "business"},
        {"business", "vip"},
        kOfferId,
        true,
        "CommonClassesIntersect_OrderOfferId_Matched",
    },
};

const models::TariffClasses kAllOfferClasses = {
    "econom", "comfort", "business", "ultima", "vip", "cargo", "express",
};

TEST_P(PaidSupplyTest, Basic) {
  const auto& params = GetParam();

  auto offer = fb::ValueBuilder(GetDefaultOffer());
  offer["prices"] = fb::ValueBuilder(formats::common::Type::kArray);
  for (const auto& class_ : kAllOfferClasses) {
    auto price = fb::ValueBuilder(formats::common::Type::kObject);

    price["cls"] = class_;
    if (params.offer_paid_supply_classes.count(class_)) {
      price["paid_supply_price"] = 100;
    }

    offer["prices"].PushBack(price.ExtractValue());
  }

  auto filters = fb::ValueBuilder(GetDefaultMatchFilters());
  if (params.order_offer_id) {
    filters["offer_id"] = *params.order_offer_id;
  }
  filters["order"]["classes"] = params.order_classes;

  const auto offer_matcher = GetDefaultOfferMatcher();

  EXPECT_EQ(offer_matcher.OfferMatchesFilters(offer.ExtractValue(),
                                              filters.ExtractValue()),
            params.offer_matches);
}

INSTANTIATE_TEST_SUITE_P(OffersMatch, PaidSupplyTest,
                         testing::ValuesIn(kPaidSupplyTestValues),
                         ::utest::PrintTestName());

struct OrderExtraClassesTestParams {
  models::TariffClasses offer_classes;
  models::TariffClasses order_classes;

  bool offer_matches;

  std::string test_name;
};

class OrderExtraClassesTest
    : public testing::TestWithParam<OrderExtraClassesTestParams> {};

const std::vector<OrderExtraClassesTestParams> kOrderExtraClassesTestValues = {
    {
        {},
        {},
        true,
        "NoOfferClasses_NoOrderClasses_Matched",
    },
    {
        {},
        {"econom", "comfort", "business"},
        false,
        "NoOfferClasses_OrderClasses_NotMatched",
    },
    {
        {"econom", "comfort", "business"},
        {},
        true,
        "OfferClasses_NoOrderClasses_Matched",
    },
    {
        {"econom", "comfort", "business"},
        {"ultima", "vip"},
        false,
        "NoCommonClasses_NotMatched",
    },
    {
        {"econom", "comfort", "business"},
        {"business", "vip"},
        false,
        "CommonClassesIntersect_NotMatched",
    },
    {
        {"econom", "comfort", "business"},
        {"comfort", "business"},
        true,
        "OfferClassesContainOrderClasses_Matched",
    },
    {
        {"comfort", "business"},
        {"econom", "comfort", "business"},
        false,
        "OrderClassesContainOfferClasses_NotMatched",
    },
};

TEST_P(OrderExtraClassesTest, Basic) {
  const auto& params = GetParam();

  auto offer = fb::ValueBuilder(GetDefaultOffer());
  offer["prices"] = fb::ValueBuilder(formats::common::Type::kArray);
  for (const auto& class_ : params.offer_classes) {
    offer["prices"].PushBack(fb::MakeDoc("cls", class_));
  }

  auto filters = fb::ValueBuilder(GetDefaultMatchFilters());
  filters["order"]["classes"] = params.order_classes;

  const auto offer_matcher = GetDefaultOfferMatcher();

  EXPECT_EQ(offer_matcher.OfferMatchesFilters(offer.ExtractValue(),
                                              filters.ExtractValue()),
            params.offer_matches);
}

INSTANTIATE_TEST_SUITE_P(OffersMatch, OrderExtraClassesTest,
                         testing::ValuesIn(kOrderExtraClassesTestValues),
                         ::utest::PrintTestName());

struct RequirementsTestParams {
  models::TariffClasses order_classes;
  fb::Value order_requirements;
  fb::Value offer_requirements;

  bool offer_matches;

  std::string test_name;
};

class RequirementsTest : public testing::TestWithParam<RequirementsTestParams> {
};

const std::vector<RequirementsTestParams> kRequirementsTestValues = {
    {
        {"econom"},
        fb::MakeDoc(),
        fb::MakeDoc(),
        true,
        "EmptyClassReqs_NotPoolOrder_NoCapacity_NoPaymentTypes_Matched",
    },
    {
        {"econom"},
        fb::MakeDoc("card", true,           //
                    "coupon", "yataxi500",  //
                    "corp", true),
        fb::MakeDoc(),
        true,
        "EmptyClassReqs_NotPoolOrder_NoCapacity_PaymentTypes_Matched",
    },
    {
        {"econom"},
        fb::MakeDoc("capacity", 5,          //
                    "card", true,           //
                    "coupon", "yataxi500",  //
                    "corp", true),
        fb::MakeDoc(),
        true,
        "EmptyClassReqs_NotPoolOrder_Capacity_PaymentTypes_Matched",
    },
    {
        {"econom", "pool"},
        fb::MakeDoc(),
        fb::MakeDoc(),
        true,
        "EmptyClassReqs_PoolOrder_NoCapacity_NoPaymentTypes_Matched",
    },
    {
        {"econom", "pool"},
        fb::MakeDoc("card", true,           //
                    "coupon", "yataxi500",  //
                    "corp", true),
        fb::MakeDoc(),
        true,
        "EmptyClassReqs_PoolOrder_NoCapacity_PaymentTypes_Matched",
    },
    {
        {"econom", "pool"},
        fb::MakeDoc("capacity", 5,          //
                    "card", true,           //
                    "coupon", "yataxi500",  //
                    "corp", true),
        fb::MakeDoc(),
        false,
        "EmptyClassReqs_PoolOrder_Capacity_PaymentTypes_NotMatched",
    },
    {
        {"econom"},
        fb::MakeDoc(),
        fb::MakeDoc("business", fb::MakeDoc()),
        false,
        "MissingOrderClassFromOfferClassReqs_NotMatched",
    },
    {
        {"econom", "pool"},
        fb::MakeDoc(),
        fb::MakeDoc("econom", fb::MakeDoc()),
        false,
        "MissingSomeOrderClassesFromOfferClassReqs_NotMatched",
    },
    {
        {"econom", "business", "pool"},
        fb::MakeDoc(),
        fb::MakeDoc("econom", fb::MakeDoc(),    //
                    "business", fb::MakeDoc(),  //
                    "pool", fb::MakeDoc()),
        true,
        "AllOrderClassesInOfferClassReqs_Matched",
    },
    {
        {"econom"},
        fb::MakeDoc("ski", true),
        fb::MakeDoc("econom", fb::MakeDoc("ski", true)),
        true,
        "SingleClass_NotPoolOrder_NoCapacity_NoPaymentTypes_Matched",
    },
    {
        {"econom"},
        fb::MakeDoc("ski", true, "childchair_v2", 10),
        fb::MakeDoc("econom", fb::MakeDoc("ski", true)),
        false,
        "SingleClass_NotPoolOrder_NoCapacity_NoPaymentTypes_NotMatched",
    },
    {
        {"econom"},
        fb::MakeDoc("ski", true,   //
                    "card", true,  //
                    "capacity", 3),
        fb::MakeDoc("econom", fb::MakeDoc("ski", true,            //
                                          "coupon", "yataxi500",  //
                                          "capacity", 5)),
        true,
        "SingleClass_NotPoolOrder_Capacity_PaymentTypes_Matched",
    },
    {
        {"pool"},
        fb::MakeDoc("ski", true,   //
                    "card", true,  //
                    "capacity", 3),
        fb::MakeDoc("pool", fb::MakeDoc("ski", true,            //
                                        "coupon", "yataxi500",  //
                                        "capacity", 5)),
        false,
        "SingleClass_PoolOrder_Capacity_PaymentTypes_NotMatched",
    },
    {
        {"pool"},
        fb::MakeDoc("ski", true,   //
                    "card", true,  //
                    "capacity", 5),
        fb::MakeDoc("pool", fb::MakeDoc("ski", true,            //
                                        "coupon", "yataxi500",  //
                                        "capacity", 5)),
        true,
        "SingleClass_PoolOrder_Capacity_PaymentTypes_Matched",
    },
    {
        {"cargo"},
        fb::MakeDoc(),
        fb::MakeDoc("cargo", fb::MakeDoc("door_to_door", false)),
        true,
        "SingleClass_DoorToDoorFix_False_NoDoorToDoorInOrder_Matched",
        // https://st.yandex-team.ru/CARGODEV-6830
    },
    {
        {"cargo"},
        fb::MakeDoc(),
        fb::MakeDoc("cargo", fb::MakeDoc("door_to_door", true)),
        false,
        "SingleClass_DoorToDoorFix_True_NoDoorToDoorInOrder_NotMatched",
        // https://st.yandex-team.ru/CARGODEV-6830
    },
    {
        {"cargo"},
        fb::MakeDoc("door_to_door", false),
        fb::MakeDoc("cargo", fb::MakeDoc("door_to_door", false)),
        true,
        "SingleClass_DoorToDoorFix_False_DoorToDoorInOrder_False_Matched",
        // https://st.yandex-team.ru/CARGODEV-6830
    },
    {
        {"cargo"},
        fb::MakeDoc("door_to_door", true),
        fb::MakeDoc("cargo", fb::MakeDoc("door_to_door", false)),
        false,
        "SingleClass_DoorToDoorFix_False_DoorToDoorInOrder_True_NotMatched",
        // https://st.yandex-team.ru/CARGODEV-6830
    },
    {
        {"econom", "cargo"},
        fb::MakeDoc("door_to_door", true, "childchair_v2", 7),
        fb::MakeDoc("econom", fb::MakeDoc(),  //
                    "cargo", fb::MakeDoc("door_to_door", true)),
        true,
        "MultiClass_AllTariffSpecificRequirements_Matched",
    },
    {
        {"econom", "cargo"},
        fb::MakeDoc("ski", true,  //
                    "door_to_door", true),
        fb::MakeDoc("econom", fb::MakeDoc("ski", true),  //
                    "cargo",
                    fb::MakeDoc("ski", true,  //
                                "door_to_door", true)),
        false,
        "MultiClass_SomeNotTariffSpecificRequirements_NotMatched",
    },
    {
        {"econom", "cargo"},
        fb::MakeDoc("yellowcarnumber", true),
        fb::MakeDoc("econom", fb::MakeDoc("yellowcarnumber", true),  //
                    "cargo", fb::MakeDoc("yellowcarnumber", true)),
        false,
        "MultiClass_AllNotTariffSpecificRequirements_NotMatched",
    },
};

TEST_P(RequirementsTest, Basic) {
  const auto& params = GetParam();

  auto offer = fb::ValueBuilder(GetDefaultOffer(params.order_classes));
  offer["classes_requirements"] = params.offer_requirements;

  auto filters = fb::ValueBuilder(GetDefaultMatchFilters());
  filters["order"]["classes"] = params.order_classes;
  filters["order"]["requirements"] = params.order_requirements;

  const auto offer_matcher = GetDefaultOfferMatcher();

  EXPECT_EQ(offer_matcher.OfferMatchesFilters(offer.ExtractValue(),
                                              filters.ExtractValue()),
            params.offer_matches);
}

INSTANTIATE_TEST_SUITE_P(OffersMatch, RequirementsTest,
                         testing::ValuesIn(kRequirementsTestValues),
                         ::utest::PrintTestName());

}  // namespace order_offers::core
