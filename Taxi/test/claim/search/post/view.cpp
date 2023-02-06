#include "view.hpp"

#include <yt_pg/criterias.hpp>
#include <yt_pg/search.hpp>

namespace handlers::v1_test_claim_search::post {

namespace {

static const std::string kHandleUrl = "/test/claims/search";

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  std::optional<handlers::TestSearchDiagnostics> diagnostics =
      handlers::TestSearchDiagnostics{};
  const auto yt_pg_criterias = cargo_claims::yt_pg::ToSearchClaimsCriterias(
      dependencies, request.body.criterias, request.body.limit,
      request.body.offset);
  const auto claims = cargo_claims::yt_pg::Search(yt_pg_criterias, dependencies,
                                                  kHandleUrl, diagnostics);
  return Response200{{claims, diagnostics.value()}};
}

}  // namespace handlers::v1_test_claim_search::post
