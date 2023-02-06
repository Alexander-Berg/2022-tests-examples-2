#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <models/handler_storage.hpp>

TEST(HandlerStorage, ByTemplate) {
  api_proxy::models::Handler handler_1{};
  // will use method as a tag
  handler_1.method_ = server::http::HttpMethod::kGet;
  api_proxy::models::Handler handler_2{};
  handler_2.method_ = server::http::HttpMethod::kPost;
  api_proxy::models::HandlerStorage handler_storage;
  handler_storage.ByTemplate("/endpoint/api").handlers.push_back(handler_1);
  handler_storage.ByTemplate("/endpoint2/api").handlers.push_back(handler_2);
  ASSERT_EQ(1, handler_storage.ByTemplate("/endpoint/api").handlers.size());
  ASSERT_EQ(
      handler_1.method_,
      handler_storage.ByTemplate("/endpoint/api").handlers.front().method_);
  ASSERT_EQ(1, handler_storage.ByTemplate("/endpoint2/api").handlers.size());
  ASSERT_EQ(
      handler_2.method_,
      handler_storage.ByTemplate("/endpoint2/api").handlers.front().method_);
}

UTEST(HandlerStorage, Match) {
  api_proxy::models::Handler handler_1{};
  handler_1.method_ = server::http::HttpMethod::kGet;
  api_proxy::models::Handler handler_2{};
  handler_2.method_ = server::http::HttpMethod::kPost;
  api_proxy::models::Handler handler_3{};
  handler_3.method_ = server::http::HttpMethod::kPut;
  api_proxy::models::Handler handler_4{};
  handler_4.method_ = server::http::HttpMethod::kDelete;
  api_proxy::models::Handler handler_5{};
  handler_5.method_ = server::http::HttpMethod::kPatch;
  api_proxy::models::HandlerStorage handler_storage;
  handler_storage.ByTemplate("/endpoint/api").handlers.push_back(handler_1);
  handler_storage.ByTemplate("/endpoint/api/(abc.*)")
      .handlers.push_back(handler_2);
  handler_storage.ByTemplate("/endpoint/api1").handlers.push_back(handler_3);
  handler_storage.ByTemplate("/endpoint/api2/").handlers.push_back(handler_4);
  handler_storage.ByTemplate("/endpoint/api3_").handlers.push_back(handler_5);

  auto result1 = handler_storage.Match("/endpoint/api");
  ASSERT_TRUE(result1);
  ASSERT_EQ(result1->handlers_[0].method_, server::http::HttpMethod::kGet);
  auto result2 = handler_storage.Match("/endpoint/api/");
  ASSERT_TRUE(result2);
  ASSERT_EQ(result2->handlers_[0].method_, server::http::HttpMethod::kGet);
  auto result3 = handler_storage.Match("/endpoint/api/abc");
  ASSERT_TRUE(result3);
  ASSERT_EQ(result3->handlers_[0].method_, server::http::HttpMethod::kPost);
  auto result4 = handler_storage.Match("/endpoint/api1");
  ASSERT_TRUE(result4);
  ASSERT_EQ(result4->handlers_[0].method_, server::http::HttpMethod::kPut);
  auto result5 = handler_storage.Match("/endpoint/api2");
  ASSERT_TRUE(result5);
  ASSERT_EQ(result5->handlers_[0].method_, server::http::HttpMethod::kDelete);
  auto result6 = handler_storage.Match("/endpoint/api3_/");
  ASSERT_TRUE(result6);
  ASSERT_EQ(result6->handlers_[0].method_, server::http::HttpMethod::kPatch);
}
