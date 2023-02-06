#include "view.hpp"

#include <userver/storages/postgres/cluster.hpp>

#include <handlers/dependencies.hpp>
#include <utils/archive_claim_recovery.hpp>
#include <utils/db/exceptions.hpp>
#include <utils/logging.hpp>

namespace handlers::v1_test_claim_recovery::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  cargo_claims::logging::AddClaimId(request.claim_id);

  const auto& cluster = dependencies.pg_cargo_claims->GetCluster();

  auto trx =
      cluster->Begin(storages::postgres::ClusterHostType::kMaster,
                     storages::postgres::TransactionOptions{
                         storages::postgres::TransactionOptions::kReadWrite});

  try {
    cargo_claims::archive_claim_recovery::ArchiveClaimRecovery(
        request.claim_id, trx, dependencies, "recovery-test");
    trx.Commit();
  } catch (cargo_claims::db::NoSuchClaimError) {
    return Response404{{ErrorWithMessageCode::kNotFound, "Claim not found"}};
  }

  return Response200{};
}

}  // namespace handlers::v1_test_claim_recovery::post
