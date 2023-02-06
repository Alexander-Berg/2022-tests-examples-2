#include "publishers_impl.hpp"

namespace geobus::publishers {

class ClientAggregatingPublisherTester {
 public:
  using AddressId = channels::AddressId;

  template <class HighLevelType>
  static bool PeriodicTaskOfChannelIsRunning(const PublishersImpl& publisher,
                                             const AddressId& address_id) {
    return publisher
        .GetAggregatingPublisherForChannel<HighLevelType>(address_id)
        .pimpl_->TaskIsRunning();
  }

  template <class HighLevelType>
  static void StopPeriodicTask(const PublishersImpl& publisher,
                               const AddressId& address_id) {
    publisher.GetAggregatingPublisherForChannel<HighLevelType>(address_id)
        .pimpl_->Stop();
  }
};

}  // namespace geobus::publishers
