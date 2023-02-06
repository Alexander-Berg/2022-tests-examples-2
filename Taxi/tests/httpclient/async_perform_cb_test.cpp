#include <gtest/gtest.h>

#include <curl-asio/multi.h>
#include <httpclient/request.hpp>
#include <httpclient/response.hpp>
#include <httpclient/statistics.hpp>
#include <threads/async.hpp>

const size_t kPoolSize = 2;

TEST(http_request, async_perform) {
  utils::http::Statistics statistics;
  utils::Async async(kPoolSize, "test", false);
  auto req_stats = std::make_shared<utils::http::RequestStats>(statistics);
  curl::multi curl_multi(async.GetIoService());
  auto request =
      std::make_shared<utils::http::Request>(curl_multi, async, req_stats);
  request->url("http://127.0.0.255");
  auto cb_promise = std::make_shared<std::promise<bool>>();
  auto cb_future = cb_promise->get_future();
  auto future = request->async_perform(
      [cb_promise](boost::system::error_code,
                   std::shared_ptr<utils::http::Response>) {
        cb_promise->set_value(true);
      },
      LogExtra());
  bool error = false;
  try {
    future.get();
  } catch (const std::exception& ex) {
    error = true;
    // connection error
  }
  ASSERT_TRUE(error);
  ASSERT_TRUE(cb_future.get());
}

TEST(http_request, async_perform_with_empty_cb) {
  utils::http::Statistics statistics;
  utils::Async async(kPoolSize, "test", false);
  auto req_stats = std::make_shared<utils::http::RequestStats>(statistics);
  curl::multi curl_multi(async.GetIoService());
  auto request =
      std::make_shared<utils::http::Request>(curl_multi, async, req_stats);
  request->url("http://127.0.0.255");
  auto future = request->async_perform(nullptr, LogExtra());
  bool error = false;
  try {
    future.get();
  } catch (const std::exception& ex) {
    error = true;
    // connection error
  }
  ASSERT_TRUE(error);
}
