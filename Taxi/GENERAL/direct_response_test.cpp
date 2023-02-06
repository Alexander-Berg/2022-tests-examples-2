#include "direct_response.hpp"
#include <gtest/gtest.h>

namespace eats_restapp_marketing::utils {

TEST(FetchDirectError, no_message) {
  clients::direct::json_v5_campaignsext::post::Response response;
  auto error = FetchDirectError(response.result);
  ASSERT_FALSE(error.has_value());
}

TEST(FetchDirectError, suspend_error) {
  clients::direct::json_v5_campaignsext::post::Response response;
  response.result = clients::direct::ResponseResult{};

  clients::direct::IdResult res;
  res.id = 1;
  res.errors = {{7, "suspend error", "suspend details"}};
  response.result->suspendresults = {res};

  auto error = FetchDirectError(response.result);
  ASSERT_TRUE(error.has_value());
  ASSERT_EQ(error->message, "suspend error");
}

TEST(FetchDirectError, resume_error) {
  clients::direct::json_v5_campaignsext::post::Response response;
  response.result = clients::direct::ResponseResult{};

  clients::direct::IdResult res;
  res.id = 1;
  res.errors = {{7, "suspend error", "suspend details"}};
  response.result->suspendresults = {res};

  res.id = 2;
  res.errors = {{7, "resume error", "resume details"}};
  response.result->resumeresults = {res};

  auto error = FetchDirectError(response.result);
  ASSERT_TRUE(error.has_value());
  ASSERT_EQ(error->message, "resume error");
}

}  // namespace eats_restapp_marketing::utils
