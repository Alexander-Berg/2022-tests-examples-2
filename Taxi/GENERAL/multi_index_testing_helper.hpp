#include "api-over-data/models/bucket_locked_replica.hpp"

namespace utils {

template <class Traits>
class BucketLockedReplicaTestingHelper {
  api_over_data::models::BucketLockedReplica<Traits>& model_;
  using ElementPtr = std::shared_ptr<const typename Traits::Element>;

 public:
  BucketLockedReplicaTestingHelper(
      api_over_data::models::BucketLockedReplica<Traits>& model)
      : model_(model) {}

  void Upsert(const ::mongo::BSONObj& doc) {
    uint32_t _;
    bool bool_;
    return model_.Upsert(doc, _, _, bool_, bool_);
  }

  void MarkReady() { model_.MarkReady(); }
};

}  // namespace utils
