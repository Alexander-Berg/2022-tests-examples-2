
#include <gtest/gtest.h>

#include <string>

struct RouterTestFixture : public ::testing::Test {
  RouterTestFixture() {
    http = clients::routing::utest::CreateHttpTvmClient();
    config_storage = clients::routing::utest::CreateRouterConfig();
  }

  std::string base_url = "http://maps.example.com";
  std::string matrix_url = "";
  std::shared_ptr<clients::Http> http;
  dynamic_config::StorageMock config_storage;
};
