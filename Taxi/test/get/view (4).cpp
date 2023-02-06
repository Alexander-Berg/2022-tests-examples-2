#include <views/autogen/https/test/get/view.hpp>

#include <clients/https-cert-sample/client.hpp>

namespace handlers::autogen_https_test::get {

namespace {

// HTTPS is slow to handshake in case of build agents under pressure.
constexpr std::chrono::seconds KSlowBuildAgentHttpsTimeout(10);

}  // namespace

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  try {
    clients::codegen::CommandControl cc;
    cc.timeout = KSlowBuildAgentHttpsTimeout;
    cc.retries = 1;  // Make sure that first HTTPS handshake succeeds.

    auto result = dependencies.https_cert_sample_client.HttpsTestOk(cc);
    return Response200{std::move(result.message)};
  } catch (const std::exception& e) {
    return Response200{std::string("Error: ") + e.what()};
  }
}

}  // namespace handlers::autogen_https_test::get
