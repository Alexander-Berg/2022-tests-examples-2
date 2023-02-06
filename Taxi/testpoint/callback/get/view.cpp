#include <views/autogen/testpoint/callback/get/view.hpp>

#include <userver/testsuite/testpoint.hpp>

namespace handlers::autogen_testpoint_callback::get {

Response View::Handle(Request&& /*request*/, Dependencies&& /*dependencies*/) {
  Response200 response;
  std::string subj = "world";

  // Testsuite supports calling user function with json::Value returned
  // from pytest testpoint handler. Callback could be used to modify normal
  // code control flow: change data, throw exceptions.
  //
  // Use as a last resort soulution. Usually there is a better way.
  // If in doubt please contact testsuite suport team.
  TESTPOINT_CALLBACK("callback_sample", formats::json::Value{},
                     [&subj](const formats::json::Value& doc) {
                       if (doc.IsObject()) {
                         if (doc.HasMember("subject")) {
                           subj = doc["subject"].As<std::string>();
                         }
                       }
                     });
  response.message = "Hello, " + subj;
  return response;
}

}  // namespace handlers::autogen_testpoint_callback::get
