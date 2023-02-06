#include "drive_order_flow_common_test.hpp"

#include <userver/formats/json.hpp>

#include <userver/logging/log.hpp>

namespace routestats::plugins::drive_order_flow::test {

namespace {
const std::string kDriveResponseSimple{R"(
  {
    "cars": [
      {
        "deeplink": "yandexdrive://cars/т577нх799",
        "location": {
          "course": 358,
          "lat": 55.77193853,
          "lon": 49.23548301
        },
        "model_id": "renault_kaptur",
        "number": "т577нх799",
        "telematics": {
          "fuel_distance": 369,
          "fuel_level": 71
        },
        "view": 0
      }
    ],
    "is_registred": true,
    "is_service_available": true,
    "offers": [
      {
        "button_text": "Забронировать",
        "cashback_prediction": 900,
        "deeplink": "yandexdrive://cars/т577нх799?offer_id=3e29f7f7-8a7d26c2-4359f132-d6e0ee72",
        "localized_free_reservation_duration": "16 мин",
        "localized_price": "74 ₽",
        "localized_riding_duration": "8 мин",
        "localized_walking_duration": "9 мин",
        "model": "Renault Kaptur",
        "model_id": "renault_kaptur",
        "number": "т577нх799",
        "offer_id": "3e29f7f7-8a7d26c2-4359f132-d6e0ee72",
        "offer_type": "fix_point",
        "price": 7400,
        "price_undiscounted": 10000,
        "riding_duration": 516,
        "walking_duration": 540
      }
    ],
    "views": [
      {
        "code": "renault_kaptur",
        "image_angle_url": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/renault-kaptur-new-kaz.png",
        "image_large_url": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/renault-kaptur-side-2-kaz_large.png",
        "image_map_url_2x": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/map-2x.png?r=3",
        "image_map_url_3x": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/map-3x.png?r=3",
        "image_pin_url_2x": "https://carsharing.s3.yandex.net/autoupload/renault_kaptur/1581340232/2white-map-pin__feb2020@2x.png",
        "image_pin_url_3x": "https://carsharing.s3.yandex.net/autoupload/renault_kaptur/1581340232/2white-map-pin__feb2020@3x.png",
        "image_small_url": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/renault-kaptur-side-2-kaz_small.png",
        "name": "Renault Kaptur",
        "meta": {
          "yandexgo_image_4x": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
        },
        "short_name": "Kaptur"
      }
    ]
  })"};

const geometry::Position point_a{35.5 * geometry::lon, 55.5 * geometry::lat};
const geometry::Position point_b{35.6 * geometry::lon, 55.7 * geometry::lat};
const geometry::Position location{35.1 * geometry::lon, 55.1 * geometry::lat};

DriveResponse MakeDriveResponseFromJson(const std::string& json) {
  auto drive_response =
      formats::json::FromString(json)
          .As<clients::yandex_drive::offers_offer_type::post::Response>();
  drive_response.x_req_id = "req_id";
  return drive_response;
}

}  // namespace

MockYandexDriveClient::MockYandexDriveClient(OffersHandler handler)
    : handler_(std::move(handler)) {}

MockYandexDriveClient::MockYandexDriveClient(DriveResponse response)
    : handler_([response = std::move(response)](const DriveRequest&) {
        return response;
      }) {}

void MockYandexDriveClient::SetHandler(OffersHandler handler) {
  handler_ = std::move(handler);
}

DriveResponse MockYandexDriveClient::OffersOfferType(
    const DriveRequest& request,
    const clients::yandex_drive::CommandControl&) const {
  return handler_(request);
}

DriveResponseBuilder::DriveResponseBuilder()
    : response_(MakeDriveResponseFromJson(kDriveResponseSimple)) {}

DriveResponseBuilder::DriveResponseBuilder(const std::string& base_json)
    : response_(MakeDriveResponseFromJson(base_json)) {}

DriveResponse DriveResponseBuilder::GetResponse() const { return response_; }

DriveResponseBuilder& DriveResponseBuilder::NoOffers(
    const std::string& reason_code) {
  response_.offers.clear();
  response_.reason_code = reason_code;
  return *this;
}

DriveResponseBuilder& DriveResponseBuilder::NotRegistered() {
  response_.is_registred = false;
  for (auto& offer : response_.offers) {
    offer.offer_id = std::nullopt;
  }
  return *this;
}

DriveResponseBuilder& DriveResponseBuilder::HasActiveSessions() {
  response_.active_session_ids = std::vector<std::string>{"smth"};
  return *this;
}

full::User MakeUser() {
  full::User user;
  user.auth_context.app_vars = std::unordered_map<std::string, std::string>{
      {ua_parser::AppVars::kVarAppName, "android"}};
  user.auth_context.locale = "ru";
  user.auth_context.flags.has_portal = true;
  user.auth_context.user_ticket = "user_ticket";
  user.auth_context.yandex_taxi_userid = "user_id";

  user.appmetrica_device_id = "device_id";
  return user;
}

handlers::RoutestatsRequest MakeRoutestatsRequest(
    const RoutestatsRequestOverrides& overrides) {
  handlers::RoutestatsRequest request;
  request.route.emplace();
  request.route->push_back(point_a);
  request.route->push_back(point_b);
  request.size_hint = 500;
  request.state.emplace();
  request.state->location = location;
  request.state->fields.push_back({"b", "b_field_title"});
  request.tariff_requirements.emplace();
  request.tariff_requirements->push_back({"drive", {}});
  request.payment.emplace();
  request.payment->type = "card";
  request.payment->payment_method_id = "card-x11546649ac1c4a3b6fcf03c2";
  request.summary_context.emplace();
  request.summary_context->by_classes = overrides.by_classes;
  return request;
}

}  // namespace routestats::plugins::drive_order_flow::test
