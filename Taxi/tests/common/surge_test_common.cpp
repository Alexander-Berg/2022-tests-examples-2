#include "surge_test_common.hpp"

namespace surge {
namespace models {

bool operator==(const SurgeValue& lhs, const SurgeValue& rhs) {
  return lhs.surge == rhs.surge && lhs.weight == rhs.weight;
}

bool operator==(const SurgeTimings& lhs, const SurgeTimings& rhs) {
  return lhs.eta == rhs.eta && lhs.etr == rhs.etr && lhs.weight == rhs.weight;
}

}  // namespace models
}  // namespace surge

namespace boost {
namespace geometry {
namespace model {

std::ostream& operator<<(std::ostream& os,
                         const surge::models::SurgeValueMapIndex::Box& box) {
  os << "[" << box.min_corner() << ";" << box.max_corner() << "]";
  return os;
}

}  // namespace model
}  // namespace geometry
}  // namespace boost
