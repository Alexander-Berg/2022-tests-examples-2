#include <arcadia_userver_test/sql_queries.hpp>
#include <userver/storages/postgres/cluster.hpp>

#include "view.hpp"

namespace handlers::databases_postgres_insert::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  auto cluster = dependencies.pg_arcadia_test->GetCluster();

  auto result =
      cluster->Execute(storages::postgres::ClusterHostType::kMaster,
                       arcadia_userver_test::sql::kInsert, request.body);

  if (result.IsEmpty()) return response;

  response.entry_id = result.AsSingleRow<std::int64_t>();

  return response;
}

// Uncomment this definition and implement the function to provide a custom
// formatter for Request body
/*
std::string View::GetRequestBodyForLogging(
  const Request* request,
    const std::string& request_body) {
  // TODO Add your code here
}
*/

// Uncomment this definition and implement the function to provide a custom
// formatter for Response data
/*
std::string View::GetResponseDataForLogging(
  const Response* response,
  const std::string& response_data) {
  // TODO Add your code here
}
*/

}  // namespace handlers::databases_postgres_insert::post
