#include "view.hpp"

#include <yt_pg/read.hpp>

namespace handlers::v1_test_claim_cut::post {

const std::string kHandleUrl = "/test/claim/cut";

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  return Response200{cargo_claims::yt_pg::GetCutByUuid(
      dependencies, request.body.uuids, kHandleUrl)};
}

}  // namespace handlers::v1_test_claim_cut::post
