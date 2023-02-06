#include <memory>

#include <gtest/gtest.h>

#include <clients/authenticators/access_key.hpp>
#include <clients/authenticators/tvm.hpp>
#include <clients/s3common.hpp>
#include <utils/tvm/tvm.hpp>

namespace {
class MockTvmTicketProvider : public tvm::TVMTicketProvider {
 public:
  std::string GetTicket() const final { return "tvm_ticket"; }
};

using TestAccessKey = ::testing::TestWithParam<clients::s3api::Request>;
}  // namespace

TEST(s3auth, TestTvm) {
  const std::string service_id{"service_id"};
  const std::string client_id{"client_id"};
  auto tvm_ticket_provider = std::make_unique<MockTvmTicketProvider>();

  auto auth_headers =
      clients::s3api::authenticators::Tvm{tvm_ticket_provider.get(), service_id,
                                          client_id}
          .Auth(clients::s3api::Request{
              {}, "", "", "", utils::http::HttpMethod::GET});

  const std::string access_key = "S3MDS_V2_" + service_id;
  ASSERT_EQ(auth_headers["Authorization"],
            "AWS " + access_key + ":DUMMY_SIGNATURE");
  ASSERT_NE(auth_headers["x-amz-security-token"].find("Ticket:"),
            std::string::npos);
  ASSERT_NE(auth_headers["x-amz-security-token"].find(client_id),
            std::string::npos);
  ASSERT_NE(auth_headers["x-amz-security-token"].find(
                tvm_ticket_provider->GetTicket()),
            std::string::npos);
}

TEST_P(TestAccessKey, Basic) {
  const std::string access_key{"access_key"};
  const std::string secret_key{"secret_key"};
  auto param = GetParam();

  auto auth_headers =
      clients::s3api::authenticators::AccessKey{access_key, secret_key}.Auth(
          param);

  ASSERT_TRUE(auth_headers.count("Date"));
  ASSERT_TRUE(auth_headers.count("Authorization"));
  ASSERT_EQ(!param.body.empty(), !!auth_headers.count("Content-MD5"));
  ASSERT_STREQ(("AWS " + access_key).c_str(),
               auth_headers["Authorization"]
                   .substr(0, auth_headers["Authorization"].find(':'))
                   .c_str());
}

INSTANTIATE_TEST_CASE_P(s3auth, TestAccessKey,
                        ::testing::Values(
                            clients::s3api::Request{
                                {},
                                "",
                                "test_bucket",
                                "user/100500",
                                utils::http::HttpMethod::GET,
                            },
                            clients::s3api::Request{
                                {},
                                "test_data",
                                "test_bucket",
                                "user/100500",
                                utils::http::HttpMethod::PUT,
                            }), );
