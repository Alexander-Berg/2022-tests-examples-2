#include "view.hpp"
#include "common/common.hpp"

#include <db/queries.hpp>
#include <defs/definitions.hpp>

#include <userver/logging/log.hpp>

namespace handlers::applications_test_v1_get_application_track_id::post {

namespace {

const std::string kRequest =
    "POST applications-test/v1/get_application_track_id";

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  bank_audit_logger::SenderInfo sender_info;
  sender_info.user_agent = request.user_agent.value_or("");
  sender_info.referrer = request.referer.value_or("");
  if (request.optional_service_info) {
    sender_info.service = request.optional_service_info->GetSourceServiceName();
  }
  dependencies.bank_audit_logger.LogHTTPRequest(
      common::kServiceName, std::chrono::system_clock::now(),
      tracing::Span::CurrentSpan(), kRequest, sender_info);
  const auto& cluster = dependencies.pg_bank_applications->GetCluster();
  const auto& config = dependencies.config;

  auto application = bank_applications::db::SelectApplication(
      cluster, config, request.body.application_id);

  if (!application) {
    LOG_WARNING() << fmt::format(
        "Cant find application with application_id({})",
        boost::uuids::to_string(request.body.application_id));
    dependencies.bank_audit_logger.LogHTTPResponse(
        common::kServiceName, std::chrono::system_clock::now(),
        tracing::Span::CurrentSpan(), "404");
    return Response404({"NotFound", "Application not found"});
  }

  if (application->additional_params &&
      application->additional_params->HasMember(bank_applications::kTrackId)) {
    const std::string track_id =
        (*application->additional_params)[bank_applications::kTrackId]
            .As<std::string>();

    dependencies.bank_audit_logger.LogHTTPResponse(
        common::kServiceName, std::chrono::system_clock::now(),
        tracing::Span::CurrentSpan(), "200");
    return Response200{track_id};
  } else {
    dependencies.bank_audit_logger.LogHTTPResponse(
        common::kServiceName, std::chrono::system_clock::now(),
        tracing::Span::CurrentSpan(), "200");
    return {};
  }
}

}  // namespace handlers::applications_test_v1_get_application_track_id::post
