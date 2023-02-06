#include <views/testonly/callsyncprocedure/post/view.hpp>

#include <clients/corp-billing-orders/client.hpp>
#include <internal/process_queue.hpp>
#include <taxi_config/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/logging/log.hpp>

namespace handlers::testonly_callsyncprocedure::post {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  auto cluster = dependencies.pg_corp_billing_orders->GetCluster();
  auto config = dependencies.config.Get<taxi_config::TaxiConfig>();

  auto pending_count = internal::ProcessQueue(
      cluster, dependencies.corp_billing_orders_client, config);
  LOG_INFO() << "Pending orders left: " << pending_count;

  return Response200{PendingCount{pending_count}};
}

}  // namespace handlers::testonly_callsyncprocedure::post
