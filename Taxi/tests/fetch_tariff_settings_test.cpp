#include <clients/taxi-tariffs/client_mock_base.hpp>
#include <tariff_settings/models.hpp>
#include <tariff_settings/utils.hpp>

#include <functional>

#include <userver/utest/utest.hpp>

namespace {
namespace tariffs = clients::taxi_tariffs;
using Request = tariffs::v1_tariff_settings_list::get::Request;
using Response = tariffs::v1_tariff_settings_list::get::Response;
using Exception = tariffs::v1_tariff_settings_list::get::Exception;
using ListResponse = tariffs::TariffSettingsListResponse;

class MockTariffsClient : public tariffs::ClientMockBase {
  using Handler = std::function<ListResponse(const Request&)>;

 public:
  MockTariffsClient(Handler handler) : ClientMockBase(), handler_(handler) {}
  Response tariffSettingsList(const Request& request,
                              const tariffs::CommandControl&) const override {
    return Response(handler_(request));
  }

 private:
  Handler handler_;
};

}  // namespace

namespace taxi_tariffs {

ListResponse MockResponse(const std::string& cursor,
                          const std::vector<std::string>& zones) {
  std::vector<models::TariffSettings> items;
  for (auto& zone : zones) items.push_back({zone, zone});
  return ListResponse{cursor, items};
}

UTEST(TestFetchBulk, EndlessPagination) {
  MockTariffsClient client([](const Request&) {
    models::TariffSettings item;
    return ListResponse{"next", {item}};
  });

  ASSERT_THROW(FetchTariffSettingsBulk(client, std::nullopt, true),
               TariffSettingsError);
}

UTEST(TestFetchBulk, TariffSettingsError) {
  MockTariffsClient client(
      [](const Request&) -> ListResponse { throw Exception(); });

  ASSERT_THROW(FetchTariffSettingsBulk(client, std::nullopt, true),
               TariffSettingsError);
}

UTEST(TestFetchBulk, Ok) {
  MockTariffsClient client([](const Request& request) -> ListResponse {
    if (!request.cursor) {
      return MockResponse("next_1", {"moscow", "spb"});
    } else if (*request.cursor == "next_1") {
      return MockResponse("next_2", {"orel"});
    } else if (*request.cursor == "next_2") {
      return MockResponse("final", {"moscow"});
    } else {
      return MockResponse("final", {});
    }
  });

  auto bulk = FetchTariffSettingsBulk(client, std::nullopt, true);
  ASSERT_EQ(bulk.next_cursor, "final");
  ASSERT_EQ(bulk.zones.size(), 4);

  bulk = FetchTariffSettingsBulk(client, "next_1", true);
  ASSERT_EQ(bulk.next_cursor, "final");
  ASSERT_EQ(bulk.zones.size(), 2);

  bulk = FetchTariffSettingsBulk(client, "next_2", true);
  ASSERT_EQ(bulk.next_cursor, "final");
  ASSERT_EQ(bulk.zones.size(), 1);

  bulk = FetchTariffSettingsBulk(client, "final", true);
  ASSERT_EQ(bulk.next_cursor, "final");
  ASSERT_EQ(bulk.zones.size(), 0);
}

}  // namespace taxi_tariffs
