#include <userver/utest/utest.hpp>

#include <userver/logging/log.hpp>
#include <userver/utest/http_client.hpp>

#include <tvm2/client.hpp>
#include <tvm2/models/impl/service_context.hpp>
#include <tvm2/models/impl/user_context.hpp>

// For manual testing only
// Set TVM_SERVICE_ID, TVM_SECRET env vars from any unstable secdist
//
// DON'T USE WITH PRODUCTION SECRETS!
//
UTEST(Tvm2, DISABLED_ServiceSmoke) {
  auto httpclient = utest::CreateHttpClient();

  auto* tvm_secret_ptr = getenv("TVM_SECRET");
  ASSERT_NE(tvm_secret_ptr, nullptr) << "TVM_SECRET env var is not set";
  std::string tvm_secret(tvm_secret_ptr);

  auto* tvm_service_id_ptr = getenv("TVM_SERVICE_ID");
  ASSERT_NE(tvm_service_id_ptr, nullptr) << "TVM_SERVICE_ID env var is not set";
  auto source_id = std::stoi(tvm_service_id_ptr);

  auto settings = std::make_shared<tvm2::ClientSettings>();
  settings->api_url = "https://tvm-api.yandex.net";
  settings->request_retries = 3;
  settings->request_timeout = std::chrono::milliseconds(10000);
  tvm2::Client client(*httpclient, settings);

  auto keys = client.DownloadKeys();
  LOG_INFO() << "keys = " << keys.GetValue();

  tvm2::models::impl::ServiceContext context(source_id, tvm_secret, keys);

  auto tickets = client.DownloadTickets(
      context, {224, 225}, tvm2::Client::PaginationSettings::kNeedAllReplies);
  for (auto it : tickets.responses) {
    auto name = it.first;
    const auto& response = it.second;
    LOG_INFO() << "name = " << name << ", value = "
               << (response.ticket ? response.ticket->GetValue()
                                   : response.error);
  }
}

UTEST(Tvm2, DISABLED_UserSmoke) {
  auto httpclient = utest::CreateHttpClient();

  auto settings = std::make_shared<tvm2::ClientSettings>();
  settings->api_url = "https://tvm-api.yandex.net";
  settings->request_retries = 3;
  settings->request_timeout = std::chrono::milliseconds(10000);
  tvm2::Client client(*httpclient, settings);

  auto keys = client.DownloadKeys();
  LOG_INFO() << "keys = " << keys.GetValue();

  tvm2::models::impl::UserContext user(keys);

  ASSERT_FALSE(
      user.Check(tvm2::models::BlackboxEnv::kTestYateam, "invalid_ticket"));
}
