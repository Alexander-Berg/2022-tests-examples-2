#pragma once

#include <clients/yandex-drive/client.hpp>
#include <clients/yandex-drive/client_mock_base.hpp>

#include "endpoints/full/core/context.hpp"
#include "endpoints/full/plugins/drive_order_flow/plugin.hpp"

#include <functional>

namespace routestats::plugins::drive_order_flow::test {

using DriveRequest = clients::yandex_drive::offers_offer_type::post::Request;
using DriveResponse = clients::yandex_drive::offers_offer_type::post::Response;

using OffersHandler = std::function<DriveResponse(const DriveRequest&)>;

struct RoutestatsRequestOverrides {
  std::optional<std::vector<handlers::ClassSummaryContext>> by_classes{};
};

class MockYandexDriveClient : public clients::yandex_drive::ClientMockBase {
 public:
  MockYandexDriveClient(OffersHandler handler);
  MockYandexDriveClient(DriveResponse response);

  void SetHandler(OffersHandler handler);

  DriveResponse OffersOfferType(
      const DriveRequest& request,
      const clients::yandex_drive::CommandControl&) const override;

 private:
  OffersHandler handler_;
};

class DriveResponseBuilder {
 public:
  explicit DriveResponseBuilder();
  DriveResponseBuilder(const std::string& base_json);

  // Returns the built response. Does not invalidate itself.
  DriveResponse GetResponse() const;

  /// Clears offers list. Results in empty offers list.
  DriveResponseBuilder& NoOffers(const std::string& reason_code);

  /// Sets is_registred flag to false and removes offers ids.
  DriveResponseBuilder& NotRegistered();

  /// Adds active sessions (rides in progress) for user.
  DriveResponseBuilder& HasActiveSessions();

 private:
  DriveResponse response_;
};

handlers::RoutestatsRequest MakeRoutestatsRequest(
    const RoutestatsRequestOverrides& overrides = {});
full::User MakeUser();

}  // namespace routestats::plugins::drive_order_flow::test
