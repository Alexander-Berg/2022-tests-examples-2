#include <string>
#include <vector>

#include <dispatch/proposition-builders/delivery/route.hpp>

namespace united_dispatch::test_helpers {

using namespace united_dispatch::waybill::delivery;
using namespace united_dispatch::models;

struct GenerateSegmentKwargs {
  bool is_valid = true;
  std::string segment_id = "segment-1";
  std::string corp_id = "";
  std::string zone_id = "";
  std::optional<std::chrono::system_clock::time_point> created_ts{};
  std::optional<std::chrono::system_clock::time_point> due{};
  bool allow_batch = true;
  bool multipoint = false;
  std::optional<std::vector<handlers::SegmentPointTimeInterval>> intervals{};
  std::optional<std::string> claim_origin{};
  std::unordered_set<std::string> claim_features_set{};
};

std::shared_ptr<united_dispatch::models::Segment> GenerateSegment(
    GenerateSegmentKwargs kwargs = {});

std::vector<Waypoint> GetPath(std::shared_ptr<Segment> segment);

std::vector<Waypoint> GetPath(
    const std::vector<std::shared_ptr<Segment>>& segments);

Route GetRouteWithSegments(const std::string& generator_name,
                           const std::vector<std::string>& segments_ids,
                           bool is_valid = true);

Route GetRouteFromSegment(std::shared_ptr<Segment> segment_ptr,
                          const std::string& generator_name = "test",
                          bool is_valid = true);

Route GetRouteFromSegments(std::vector<std::shared_ptr<Segment>> segments,
                           const std::string& generator_name = "test",
                           bool is_valid = true);

}  // namespace united_dispatch::test_helpers
