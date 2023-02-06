#include "view.hpp"

#include <yt_pg/read.hpp>

namespace handlers::v1_test_claim_full::get {

const std::string kHandleUrl = "/test/claim/full";

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  if (const auto claim = cargo_claims::yt_pg::GetByUuid(
          dependencies, request.claim_id, kHandleUrl)) {
    return Response200{claim.value()};
  }
  return Response404{{ErrorWithMessageCode::kNotFound, "Claim not found"}};
}

}  // namespace handlers::v1_test_claim_full::get
