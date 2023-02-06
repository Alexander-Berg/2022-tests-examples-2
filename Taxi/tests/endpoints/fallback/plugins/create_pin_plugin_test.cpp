
#include <functional>

#include <userver/utest/utest.hpp>

#include <clients/pin-storage/client_mock_base.hpp>

#include <endpoints/fallback/core/context.hpp>
#include <endpoints/fallback/plugins/create_pin/plugin.hpp>
#include <tests/endpoints/fallback/context/surge_mock_test.hpp>

namespace routestats::fallback {

std::vector<int> GetClientVersion(const ua_parser::AppVars& app_vars);
clients::pin_storage::Pin BuildPin(const CreatePinPluginContext& ctx);
void RegisterPin(const CreatePinPluginContext& ctx);

using V1CreatePinRequest = clients::pin_storage::v1_create_pin::put::Request;
using V1CreatePinResponse = clients::pin_storage::v1_create_pin::put::Response;
using V1CreatePinHandler = std::function<V1CreatePinResponse()>;

class MockPinStorage : public clients::pin_storage::ClientMockBase {
 public:
  MockPinStorage(const V1CreatePinHandler& create_pin_handler)
      : create_pin_handler_(create_pin_handler){};
  V1CreatePinResponse V1CreatePin(
      const V1CreatePinRequest&,
      const clients::pin_storage::CommandControl&) const override {
    return create_pin_handler_();
  }

 private:
  V1CreatePinHandler create_pin_handler_;
};

void TestRegisterPin(const V1CreatePinHandler& handler) {
  core::Zone zone{};
  fallback::User user{};
  RoutestatsRequest request{};
  auto pin_storage = std::make_shared<MockPinStorage>(handler);
  auto bts = concurrent::BackgroundTaskStorage();
  //  auto bts_wrapper =
  //  std::make_shared<core::BTSWrapper>(core::BTSWrapper{bts});

  const CreatePinPluginContext ctx{
      zone,         user, request,
      *pin_storage, bts,  std::make_shared<test::SurgeMock>(SurgeInfo{})};

  ASSERT_NO_THROW(RegisterPin(ctx));
}

UTEST(RegisterPin, HappyPath) {
  TestRegisterPin(
      []() -> V1CreatePinResponse { return V1CreatePinResponse{}; });
}

UTEST(RegisterPin, PinStorageError) {
  TestRegisterPin([]() -> V1CreatePinResponse {
    throw std::runtime_error{"pin storage error"};
  });
}

TEST(GetClientVersion, HappyPath) {
  const auto vars = ua_parser::AppVars{
      {{"app_ver1", "1"}, {"app_ver2", "2"}, {"app_ver3", "3"}}};
  auto result = GetClientVersion(vars);
  ASSERT_EQ(result, std::vector<int>({1, 2, 3}));
}

TEST(GetClientVersion, SmthMissed) {
  const auto vars = ua_parser::AppVars{{{"app_ver1", "1"}, {"app_ver2", "2"}}};
  auto result = GetClientVersion(vars);
  ASSERT_EQ(result, std::vector<int>({1, 2, 0}));
}

UTEST(BuildPin, HappyPath) {
  core::Zone zone{};
  zone.zone_name = "kislovodsk";

  fallback::User user{};
  user.auth_context.yandex_taxi_userid = "1234";
  user.auth_context.personal.phone_id = "56789";
  user.auth_context.app_vars = ua_parser::AppVars{
      {{"app_ver1", "3"}, {"app_ver3", "1"}, {"app_name", "nokia"}}};

  RoutestatsRequest request{};
  request.route = std::vector<geometry::Position>{
      {37.2 * geometry::lon, 55.5 * geometry::lat}};
  request.selected_class = "ultima";

  auto pin_storage = std::make_shared<MockPinStorage>(
      []() -> V1CreatePinResponse { return V1CreatePinResponse{}; });
  auto bts = concurrent::BackgroundTaskStorage();

  auto ctx = CreatePinPluginContext{
      zone,    user,
      request, *pin_storage,
      bts,     std::make_shared<test::SurgeMock>(SurgeInfo{"idd", {}})};

  auto result = BuildPin(ctx);
  ASSERT_EQ(result.user_id, "1234");
  ASSERT_EQ(result.personal_phone_id, "56789");
  ASSERT_EQ(result.tariff_zone, "kislovodsk");
  ASSERT_EQ(result.point_a.

            value(),
            geometry::PositionAsArray(geometry::Longitude{37.2},
                                      geometry::Latitude{55.5})

  );
  ASSERT_EQ(result.client->name, "nokia");
  ASSERT_EQ(result.client->version, std::vector<int>({3, 0, 1}));
  ASSERT_EQ(result.user_layer, "default");
  ASSERT_EQ(result.calculation_id, "idd");
}
}  // namespace routestats::fallback
