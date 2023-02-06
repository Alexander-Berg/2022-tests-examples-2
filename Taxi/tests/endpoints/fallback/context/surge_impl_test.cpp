
#include <functional>

#include <userver/utest/utest.hpp>

#include <clients/surge-calculator/client_mock_base.hpp>

#include <endpoints/fallback/core/context/surge/surge_impl.hpp>

namespace routestats::fallback {

using Decimal = decimal64::Decimal<4>;

using V1CalcSurgeRequest =
    clients::surge_calculator::v1_calc_surge::post::Request;
using V1CalcSurgeResponse =
    clients::surge_calculator::v1_calc_surge::post::Response;
using V1CalcSurgeHandler = std::function<V1CalcSurgeResponse()>;

class MockSurgeStorage : public clients::surge_calculator::ClientMockBase {
 public:
  MockSurgeStorage(const V1CalcSurgeHandler& calc_surge_handler)
      : calc_surge_handler_(calc_surge_handler){};
  V1CalcSurgeResponse V1CalcSurge(
      const V1CalcSurgeRequest&,
      const clients::surge_calculator::CommandControl&) const override {
    return calc_surge_handler_();
  }

 private:
  V1CalcSurgeHandler calc_surge_handler_;
};

void TestSurgeErrors(const V1CalcSurgeHandler& handler,
                     std::optional<std::vector<geometry::Position>> route) {
  RunInCoro([handler, route]() {
    MockSurgeStorage client(handler);
    passenger_authorizer::models::AuthContext pa_auth{};
    handlers::RoutestatsRequest request{};
    request.route = route;

    SurgeCalculator surger{client, request, pa_auth, "chelyabinsk",
                           std::vector<std::string>{"vip"}};
    surger.StartLoadSurge();
    surger.LoadSurge();

    ASSERT_EQ(surger.GetSurgeInfo(), std::nullopt);
  });
}

TEST(SurgerErrors, ClientError) {
  TestSurgeErrors(
      []() -> V1CalcSurgeResponse { throw std::runtime_error{"surger error"}; },
      std::nullopt);
}

TEST(SurgerErrors, NoRoute) {
  TestSurgeErrors(
      []() -> V1CalcSurgeResponse {
        auto response = V1CalcSurgeResponse{};
        response.calculation_id = "first_id";
        return response;
      },
      std::nullopt);
}

TEST(SurgerErrors, EmptyRoute) {
  TestSurgeErrors(
      []() -> V1CalcSurgeResponse {
        auto response = V1CalcSurgeResponse{};
        response.calculation_id = "first_id";
        return response;
      },
      std::vector<geometry::Position>{});
}

void AssertSurge(const Surge& lhs, const Surge& rhs) {
  ASSERT_EQ(lhs.surge, rhs.surge);
  ASSERT_EQ(lhs.surcharge.alpha, rhs.surcharge.alpha);
  ASSERT_EQ(lhs.surcharge.beta, lhs.surcharge.beta);
  ASSERT_EQ(lhs.surcharge.surcharge, lhs.surcharge.surcharge);
}

void TestSurgeHappyPaths(const V1CalcSurgeHandler& handler,
                         std::optional<std::vector<geometry::Position>> route,
                         bool has_surcharge) {
  RunInCoro([handler, route, has_surcharge]() {
    MockSurgeStorage client(handler);
    passenger_authorizer::models::AuthContext pa_auth{};
    handlers::RoutestatsRequest request{};
    request.route = route;

    SurgeCalculator surger{client, request, pa_auth, "chelyabinsk",
                           std::vector<std::string>{"vip"}};
    surger.StartLoadSurge();
    surger.LoadSurge();
    auto result = surger.GetSurgeInfo();

    ASSERT_EQ(result->calculation_id, "first_id");
    ASSERT_EQ(result->surge_map.size(), 1);
    auto expected = Surge{};
    if (has_surcharge) {
      expected = Surge{Decimal{"1.3"}, SurCharge{Decimal{"0.9"}, Decimal{"0.1"},
                                                 Decimal{"0.2"}}};
    } else {
      expected = Surge{Decimal{"1.3"},
                       SurCharge{Decimal{"1"}, Decimal{"0"}, Decimal{"0"}}};
    }
    AssertSurge(result->surge_map.at("vip"), expected);
    AssertSurge(surger.GetSurgeByCategory("vip").value(), expected);
    ASSERT_FALSE(surger.GetSurgeByCategory("the_best"));
  });
}

TEST(SurgerHappyPaths, NoSurcharge) {
  TestSurgeHappyPaths(
      []() -> V1CalcSurgeResponse {
        auto response = V1CalcSurgeResponse{};
        response.calculation_id = "first_id";
        clients::surge_calculator::ClassInfo class_info{};
        class_info.name = "vip";
        class_info.surge =
            clients::surge_calculator::PricingCoeffs{1.3, std::nullopt};
        response.classes.push_back(class_info);
        return response;
      },
      std::vector<geometry::Position>{
          {37.2 * geometry::lon, 55.5 * geometry::lat}},
      false);
}

TEST(SurgerHappyPaths, WithSurcharge) {
  TestSurgeHappyPaths(
      []() -> V1CalcSurgeResponse {
        auto response = V1CalcSurgeResponse{};
        response.calculation_id = "first_id";
        clients::surge_calculator::ClassInfo class_info{};
        class_info.name = "vip";
        class_info.surge = clients::surge_calculator::PricingCoeffs{
            1.3, clients::surge_calculator::Surcharge{0.9, 0.1, 0.2}};
        response.classes.push_back(class_info);
        return response;
      },
      std::vector<geometry::Position>{
          {37.2 * geometry::lon, 55.5 * geometry::lat}},
      true);
}

}  // namespace routestats::fallback
