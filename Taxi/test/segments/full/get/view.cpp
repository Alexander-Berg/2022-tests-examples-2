#include "view.hpp"

#include <yt_pg/read.hpp>

namespace handlers::v1_test_segments_full::get {

using namespace cargo_dispatch;

namespace {

const std::string kHandleUrl = "/v1/test/segments/full";

}

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  if (const auto data = yt_pg::GetSegmentWithWaybillBySegmentId(
          dependencies, request.segment_id, kHandleUrl)) {
    return Response200{data.value().segment, data.value().waybills};
  }
  return Response404{};
}

}  // namespace handlers::v1_test_segments_full::get
