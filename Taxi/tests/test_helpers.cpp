#include "test_helpers.hpp"

namespace {

const double kEpsilon = 0.000001;

template <typename T>
bool CompareOptionalWithEpsilon(const boost::optional<T>& lhs,
                                const boost::optional<T>& rhs) {
  if ((lhs && !rhs) || (rhs && !lhs)) {
    return false;
  }
  if (lhs && std::fabs(*lhs - *rhs) > kEpsilon) {
    return false;
  }
  return true;
};
}  // namespace

namespace models {

bool operator==(const DriverRating& lhs, const DriverRating& rhs) {
  return CompareOptionalWithEpsilon(lhs.rating, rhs.rating) &&
         lhs.rating_count == rhs.rating_count &&
         CompareOptionalWithEpsilon(lhs.total, rhs.total);
}

bool operator==(const DriverRatingInfo& lhs, const DriverRatingInfo& rhs) {
  return lhs.id == rhs.id && lhs.is_deleted == rhs.is_deleted &&
         lhs.revision == rhs.revision && lhs.data == rhs.data;
}

}  // namespace models
