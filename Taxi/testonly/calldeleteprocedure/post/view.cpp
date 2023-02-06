#include <views/testonly/calldeleteprocedure/post/view.hpp>

#include <clients/corp-billing-orders/client.hpp>
#include <internal/clear_payment_orders.hpp>
#include <taxi_config/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/logging/log.hpp>

namespace handlers::testonly_calldeleteprocedure::post {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  auto cluster = dependencies.pg_corp_billing_orders->GetCluster();
  auto config = dependencies.config.Get<taxi_config::TaxiConfig>();

  auto deleted_count = internal::ClearPaymentOrders(cluster, config);
  LOG_INFO() << "Deleted orders: " << deleted_count;

  return Response200{DeletedCount{deleted_count}};
}

}  // namespace handlers::testonly_calldeleteprocedure::post
