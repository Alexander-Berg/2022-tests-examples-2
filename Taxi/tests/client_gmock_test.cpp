#include <userver/utest/utest.hpp>

#include <clients/userver-sample/client_gmock.hpp>

namespace clients::userver_sample {

TEST(CodegenClientGMock, SimpleCall) {
  constexpr std::string_view kTestString{"test_gmock"};
  ClientGMock mock_client;
  using Response = autogen_common::get::Response200;
  using Request = autogen_common::get::Request;

  Response server_result;
  server_result.common = kTestString;

  EXPECT_CALL(mock_client, AutogenCommon)
      .WillOnce(::testing::Return(server_result));

  auto result = mock_client.AutogenCommon(Request{}, CommandControl{});
  EXPECT_EQ(kTestString, result.common);
}

}  // namespace clients::userver_sample
