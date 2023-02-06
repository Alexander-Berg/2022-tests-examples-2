#include <clients/routing/test/router_selector_mock.hpp>

#include <userver/utest/utest.hpp>

namespace clients::routing {

// Here we test that our RouterMock is actually working

TEST(RouterSelectorMockTest, Basic) {
  auto mock_object = std::make_unique<
      ::testing::NiceMock<clients::routing::RouterSelectorMock>>();
}

}  // namespace clients::routing
