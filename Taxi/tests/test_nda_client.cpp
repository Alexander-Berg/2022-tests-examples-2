#include <gtest/gtest.h>

#include <clients/nda/client_mock_base.hpp>
#include <clients/nda/detail/nda_client_impl.hpp>
#include <clients/nda/nda_client_component.hpp>

#include <atomic>

#include <userver/engine/sleep.hpp>
#include <userver/engine/task/task_with_result.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>
#include <utils/time.hpp>

namespace hejmdal {

UTEST(TestNda, NdaLoadTest) {
  /// MockClient class is used for simulation of NDA server work
  class MockClient : public ::clients::nda::ClientMockBase {
   public:
    /// @param max_requests: the maximum amount of simultaneous requests to NDA
    MockClient(size_t max_requests)
        : max_requests_to_nda_(max_requests), current_requests_amount_(0){};

    /// Overridden method of the underlying class Client
    virtual ::clients::nda::ns__::get::Response ShortenUrl(
        const ::clients::nda::ns__::get::Request&,
        const ::clients::nda::CommandControl&) const override {
      auto response_body =
          ++current_requests_amount_ <= max_requests_to_nda_ ? "OK" : "ERR";
      ::engine::SleepFor(time::Milliseconds(10));
      --current_requests_amount_;
      return ::clients::nda::ns__::get::Response{response_body};
    }

   private:
    const size_t max_requests_to_nda_;
    mutable std::atomic<size_t> current_requests_amount_;
  };  // class MockClient

  /// Function to be used for different test cases
  auto test_case = [](const auto max_requests, const auto sleep_ms) {
    MockClient mock(max_requests);
    hejmdal::clients::detail::NdaClientImpl nda_client(
        mock, max_requests, time::Milliseconds(sleep_ms));

    std::vector<engine::TaskWithResult<std::string>> futures(max_requests * 5);
    for (size_t i = 0; i < futures.size(); ++i) {
      futures[i] = ::utils::Async("shortener", [&nda_client]() {
        return nda_client.ShortenUrl("Test URL");
      });
    }
    for (auto& future : futures) {
      ASSERT_EQ("OK", future.Get());
    }
  };  // test_case

  /// Test cases

  ASSERT_NO_THROW(test_case(1, 0));
  ASSERT_NO_THROW(test_case(10, 0));
  ASSERT_NO_THROW(test_case(10, 10));
}

}  // namespace hejmdal
