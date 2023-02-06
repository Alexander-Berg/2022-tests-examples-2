#include "view.hpp"

#include <yt_pg/read.hpp>

namespace handlers::v1_test_waybills_full::get {

using namespace cargo_dispatch;

namespace {

const std::string kHandleUrl = "/v1/test/waybills/full";

}

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  if (request.external_ref) {
    if (const auto data = yt_pg::GetWaybillWithSegmentsByExternalRef(
            dependencies, request.external_ref.value(), kHandleUrl)) {
      return Response200{data.value().segments, data.value().waybill};
    }
  } else if (request.waybill_order_id) {
    if (const auto data = yt_pg::GetWaybillWithSegmentsByWaybillOrderId(
            dependencies, request.waybill_order_id.value(), kHandleUrl)) {
      return Response200{data.value().segments, data.value().waybill};
    }
  }

  return Response404{};
}

}  // namespace handlers::v1_test_waybills_full::get
