#include <gtest/gtest.h>
#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <endpoints/full/plugins/drive_order_flow/drive_offers/drive_offers_impl.hpp>

#include "tests/context_mock_test.hpp"

#include "drive_order_flow_common_test.hpp"

#include <userver/logging/log.hpp>

#include <taxi_config/variables/TARIFF_CATEGORIES_ORDER_FLOW.hpp>

namespace routestats::plugins::drive_order_flow {

namespace test {

using DriveRequest = clients::yandex_drive::offers_offer_type::post::Request;
using DriveResponse = clients::yandex_drive::offers_offer_type::post::Response;

}  // namespace test

namespace {

dynamic_config::Snapshot MakeTaxiConfig() {
  return dynamic_config::GetDefaultSnapshot();
}

struct TestData {
  std::optional<test::DriveRequest> drive_request;
  std::optional<DriveOffers> drive_offers;
};

const std::string kInvisibleTariff = "invis";

const core::CategoriesVisibility kCategoriesVisibility{
    {
        {
            "drive",
            {
                true,   // is_visible
                false,  // should_be_skipped
            },
        },
        {
            "skip",
            {
                true,  // is_visible
                true,  // should_be_skipped
            },
        },
        {
            kInvisibleTariff,
            {
                false,  // is_visible
                false,  // should_be_skipped
            },
        },
    },
    {},  // ordered_allowed_categories
};

TestData TestRequest(
    const full::User& user,
    const handlers::RoutestatsRequest& routestats_request,
    const std::optional<test::DriveResponse>& drive_response = std::nullopt) {
  std::optional<test::DriveRequest> drive_request;
  test::MockYandexDriveClient client(
      [&drive_request, &drive_response](
          const test::DriveRequest& req) -> test::DriveResponse  //
      {
        drive_request = req;
        // fails if nullopt
        return drive_response.value();
      });

  auto taxi_config = MakeTaxiConfig();

  auto drive_summary_context = GetDriveSummaryContext(routestats_request);
  DriveOffersViaYandexDrive drive(
      user, routestats_request, kCategoriesVisibility, taxi_config,
      routestats::test::GetDefaultExperiments(), client, drive_summary_context);

  drive.StartLoadingDriveOffers();
  auto drive_offers = drive.GetDriveOffersForServiceLevel("drive");

  return {std::move(drive_request), std::move(drive_offers)};
}

}  // namespace

UTEST(DriveOffersImpl, Errors) {
  const auto user = test::MakeUser();
  test::RoutestatsRequestOverrides overrides;
  handlers::ClassSummaryContext class_summary_context;
  handlers::DriveSummaryContext drive_summary_context;
  drive_summary_context.class_ = "drive";
  drive_summary_context.payload.previous_offer_ids = {"test_offer_id"};
  class_summary_context = std::move(drive_summary_context);
  overrides.by_classes.emplace();
  overrides.by_classes->push_back(class_summary_context);
  const auto [drive_request, drive_offers] =
      TestRequest(user, test::MakeRoutestatsRequest(overrides));
  ASSERT_EQ(drive_offers, std::nullopt);
  ASSERT_TRUE(drive_request);
  ASSERT_EQ(drive_request->lang, user.auth_context.locale);
  ASSERT_EQ(drive_request->src, "35.5 55.5");
  ASSERT_EQ(drive_request->dst, "35.6 55.7");
  ASSERT_EQ(drive_request->x_ya_user_ticket, "user_ticket");
  ASSERT_EQ(drive_request->destination_name, "b_field_title");
  ASSERT_EQ(drive_request->lon.value(), "35.100000");
  ASSERT_EQ(drive_request->lat.value(), "55.100000");
  ASSERT_EQ(drive_request->body.previous_offer_ids->size(), 1);
  ASSERT_EQ(drive_request->body.previous_offer_ids->front(), "test_offer_id");
}

UTEST(DriveOffersImpl, PaymentCard) {
  auto [drive_request, _] =
      TestRequest(test::MakeUser(), test::MakeRoutestatsRequest());
  ASSERT_TRUE(drive_request);
  ASSERT_TRUE(drive_request->body.payment_methods);
  ASSERT_EQ(drive_request->body.payment_methods->size(), 1);
  ASSERT_EQ(drive_request->body.payment_methods->front().account_id, "card");
  ASSERT_EQ(drive_request->body.payment_methods->front().card,
            "card-x11546649ac1c4a3b6fcf03c2");
}

UTEST(DriveOffersImpl, PaymentNone) {
  auto routestats_request = test::MakeRoutestatsRequest();
  routestats_request.payment = std::nullopt;

  auto [drive_request, _] = TestRequest(test::MakeUser(), routestats_request);
  ASSERT_TRUE(drive_request);
  ASSERT_FALSE(drive_request->body.payment_methods);
}

UTEST(DriveOffersImpl, PaymentInvalid) {
  auto routestats_request = test::MakeRoutestatsRequest();
  routestats_request.payment.emplace();
  routestats_request.payment->type = "cash";

  auto [drive_request, _] = TestRequest(test::MakeUser(), routestats_request);
  ASSERT_TRUE(drive_request);
  ASSERT_FALSE(drive_request->body.payment_methods);
}

UTEST(DriveOffersImpl, HappyPath) {
  auto [_, drive_offers] =
      TestRequest(test::MakeUser(), test::MakeRoutestatsRequest(),
                  test::DriveResponseBuilder().GetResponse());
  ASSERT_TRUE(drive_offers);
  ASSERT_EQ(drive_offers->user_type, DriveOffers::UserType::kPortalReg);
  ASSERT_EQ(drive_offers->type, DriveOffers::Type::kFull);
  ASSERT_FALSE(drive_offers->reason_code);
  ASSERT_EQ(drive_offers->offers.size(), 1);
  ASSERT_EQ(drive_offers->offers.front().price_rub, decimal64::Decimal<4>(74));
  ASSERT_EQ(drive_offers->offers.front().car_number, "т577нх799");
  ASSERT_EQ(drive_offers->offers.front().offer_id,
            "3e29f7f7-8a7d26c2-4359f132-d6e0ee72");
  ASSERT_EQ(drive_offers->offers.front().car_model_code, "renault_kaptur");
  ASSERT_EQ(drive_offers->offers.front().car_image_url,
            "https://carsharing.s3.yandex.net/drive/car-models/"
            "renault_kaptur/renault-kaptur-side-2-kaz_large.png");
  ASSERT_EQ(drive_offers->active_session_ids, std::vector<std::string>{});
}

UTEST(DriveOffersImpl, HasActiveSessions) {
  test::MockYandexDriveClient client(
      test::DriveResponseBuilder().HasActiveSessions().GetResponse());

  const auto user = test::MakeUser();
  const auto taxi_config = MakeTaxiConfig();
  const auto routestats_request = test::MakeRoutestatsRequest();

  DriveOffersViaYandexDrive drive(
      user, routestats_request, kCategoriesVisibility, taxi_config,
      routestats::test::GetDefaultExperiments(), client, std::nullopt);

  drive.StartLoadingDriveOffers();
  auto drive_offers = drive.GetDriveOffersForServiceLevel("drive");
  ASSERT_TRUE(drive_offers);
  ASSERT_EQ(drive_offers->user_type, DriveOffers::UserType::kPortalReg);
  ASSERT_EQ(drive_offers->type, DriveOffers::Type::kFull);
  ASSERT_FALSE(drive_offers->reason_code);
  ASSERT_EQ(drive_offers->offers.size(), 1);
  ASSERT_EQ(drive_offers->active_session_ids, std::vector<std::string>{"smth"});
}

UTEST(DriveOffersImpl, TariffCheck) {
  test::MockYandexDriveClient client(
      test::DriveResponseBuilder().GetResponse());

  const auto user = test::MakeUser();

  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::TARIFF_CATEGORIES_ORDER_FLOW,
       {{{kInvisibleTariff,
          taxi_config::tariff_categories_order_flow::OrderFlow{"drive"}}}}},
  });
  auto taxi_config = config_storage.GetSnapshot();

  auto routestats_request = test::MakeRoutestatsRequest();
  routestats_request.tariff_requirements = {{kInvisibleTariff, {}}};

  DriveOffersViaYandexDrive drive(
      user, routestats_request, kCategoriesVisibility, taxi_config,
      routestats::test::GetDefaultExperiments(), client, std::nullopt);

  drive.StartLoadingDriveOffers();
  auto drive_offers = drive.GetDriveOffersForServiceLevel(kInvisibleTariff);
  EXPECT_FALSE(drive_offers);
}

struct ReasonCodeTestInput {
  std::string drive_code;
  std::string routestats_code;
};

const std::vector<ReasonCodeTestInput> kReasonCodeTestInputs{
    {"ololo", "drive_no_cars"},
    {"no_cars", "drive_no_cars"},
    {"cannot_drop_car_in_destination", "drive_bad_dst"},
    {"incorrect_destination_tags", "drive_bad_dst"},
    {"router_unanswer", "drive_bad_dst"},
    {"undefined_route", "drive_bad_dst"},
    {"too_far_destination", "drive_bad_dst"},
    {"cannot_build_stop_area_info", "drive_bad_dst"},
    {"too_close_destination", "drive_too_close_dst"},
    {"too_close_destination_msk", "drive_too_close_dst"},
    {"too_close_destination_spb", "drive_too_close_dst"},
    {"too_close_destination_3", "drive_too_close_dst"},
    {"too_close_destination_2077", "drive_too_close_dst"},
    {"too_close_destinationololo", "drive_too_close_dst"},
};

class DriveOffersImplReasonCodeMapping
    : public testing::TestWithParam<ReasonCodeTestInput> {};

UTEST_P(DriveOffersImplReasonCodeMapping, AllCases) {
  auto [drive_code, routestats_code] = GetParam();

  test::MockYandexDriveClient client(
      test::DriveResponseBuilder().NoOffers(drive_code).GetResponse());

  const auto user = test::MakeUser();
  const auto taxi_config = MakeTaxiConfig();
  const auto routestats_request = test::MakeRoutestatsRequest();

  DriveOffersViaYandexDrive drive(
      user, routestats_request, kCategoriesVisibility, taxi_config,
      routestats::test::GetDefaultExperiments(), client, std::nullopt);

  drive.StartLoadingDriveOffers();
  auto drive_offers = drive.GetDriveOffersForServiceLevel("drive");
  ASSERT_TRUE(drive_offers);
  ASSERT_TRUE(drive_offers->reason_code);
  EXPECT_EQ(ToString(*drive_offers->reason_code), routestats_code);
}

INSTANTIATE_UTEST_SUITE_P(/* no prefix */, DriveOffersImplReasonCodeMapping,
                          testing::ValuesIn(kReasonCodeTestInputs));

}  // namespace routestats::plugins::drive_order_flow
