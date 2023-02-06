#include "view.hpp"

#include <userver/logging/log.hpp>
#include <userver/storages/postgres/transaction.hpp>

#include <db/pg/queries.hpp>
#include <models/exceptions.hpp>

namespace {

namespace pg = ::driver_scoring::db::pg;

}  // namespace

namespace handlers::v2_admin_scripts_tests::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const auto cluster = dependencies.pg_driver_scoring->GetCluster();
  try {
    Response200 response{{pg::FetchScriptTestsById(cluster, request.id)}};
    return response;
  } catch (const std::exception& exc) {
    LOG_ERROR() << request.id << " failed to get tests: " << exc;
    return Response404({exc.what(), 404});
  }
}

}  // namespace handlers::v2_admin_scripts_tests::get
