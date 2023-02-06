#include "fetch_driver_status.hpp"

#include <algorithm>
#include <cstdlib>
#include <iterator>
#include <memory>
#include <optional>

#include <fmt/format.h>

#include <userver/utest/utest.hpp>

#include <models/driverid.hpp>
#include <userver/engine/task/task.hpp>

#include "models/driver_statuses.hpp"

namespace cf = candidates::filters;
namespace cf_infra = cf::infrastructure;

const cf::FilterInfo kEmptyInfo;
const unsigned kStatusesRange = 3;

namespace helpers {

struct Status {
  std::string driver_id;
  std::string park_id;
  models::DriverStatus status;
};

models::DriverStatus ToStatus(int value) {
  switch (value) {
    case 0:
      return models::DriverStatus::kOffline;
    case 1:
      return models::DriverStatus::kOnline;
    case 2:
      return models::DriverStatus::kBusy;
  }
  throw std::runtime_error(fmt::format("Unknown status value: {}", value));
}

template <class Inserter>
void GenerateDriverStatuses(
    Inserter inserter, std::size_t first_idx, std::size_t last_idx,
    const std::string& driver_id_prefix = "driver",
    const std::string& park_id_prefix = "park",
    std::optional<models::DriverStatus> status = std::nullopt) {
  for (auto i = first_idx; i < last_idx; ++i) {
    const auto idx_str = std::to_string(i);
    const auto status_value =
        (status.has_value()) ? *status : ToStatus(std::rand() % kStatusesRange);
    *inserter = Status{driver_id_prefix + idx_str, park_id_prefix + idx_str,
                       status_value};
  }
}

template <class ConstIterator>
void FillStorage(models::DriverStatuses& storage, ConstIterator cbegin,
                 ConstIterator cend) {
  for (auto i = cbegin; i != cend; ++i) {
    if (i->status == models::DriverStatus::kOffline)
      storage.erase(models::DriverId::MakeDbidUuid(i->park_id, i->driver_id));
    else
      storage[models::DriverId::MakeDbidUuid(i->park_id, i->driver_id)] =
          i->status;
  }
}
}  // namespace helpers

UTEST(FetchDriverStatus, NoStatus) {
  auto storage = std::make_shared<::models::DriverStatuses>();
  cf_infra::FetchDriverStatus filter(kEmptyInfo, storage);
  cf::Context context;
  candidates::GeoMember member;
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
  EXPECT_EQ(cf_infra::FetchDriverStatus::Get(context),
            models::DriverStatus::kOffline);
}

UTEST(FetchDriverStatus, Sample) {
  auto storage = std::make_shared<::models::DriverStatuses>();
  std::vector<helpers::Status> statuses;
  helpers::GenerateDriverStatuses(std::back_inserter(statuses), 0, 1, "driver",
                                  "park", models::DriverStatus::kBusy);
  FillStorage(*storage, statuses.cbegin(), statuses.cend());
  cf_infra::FetchDriverStatus filter(kEmptyInfo, storage);
  for (const auto& item : statuses) {
    cf::Context context;
    candidates::GeoMember member;
    member.id = models::DriverId::MakeDbidUuid(item.park_id, item.driver_id);
    EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
    EXPECT_EQ(cf_infra::FetchDriverStatus::Get(context),
              models::DriverStatus::kBusy);
  }
  {
    cf::Context context;
    candidates::GeoMember member;
    member.id = models::DriverId::MakeDbidUuid("park_10", "driver_10");
    EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
    EXPECT_EQ(cf_infra::FetchDriverStatus::Get(context),
              models::DriverStatus::kOffline);
  }
}
