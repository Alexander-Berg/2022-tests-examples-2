#include "view.hpp"

#include <handlers/dependencies.hpp>
#include <yt_pg/read.hpp>

#include <components/claim_denorm_cache/component.hpp>

namespace handlers::v1_test_claim_redis_full::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  if (const auto claim = dependencies.extra.denorm_cache_component.GetClaim(
          request.claim_id)) {
    return Response200{claim.value()};
  }
  return Response404{{ErrorWithMessageCode::kNotFound, "Claim not found"}};
}

}  // namespace handlers::v1_test_claim_redis_full::get
