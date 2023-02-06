#include <gtest/gtest.h>

#include <boost/range/adaptor/map.hpp>
#include <caches/parking_drivers.hpp>

namespace dapp = ::models::dispatch::airport::partner::protocol;

namespace {

auto Time(std::time_t t) { return std::chrono::system_clock::from_time_t(t); };

caches::ParkingDriversCacheContainer CreateContainer(
    const std::vector<dapp::ParkingDriver>& drivers) {
  caches::ParkingDriversCacheContainer container;
  for (const auto& driver : drivers) {
    container.insert_or_assign({driver.driver_id, driver.parking_id},
                               dapp::ParkingDriver(driver));
  }

  return container;
}

dapp::ParkingDriver CreateDriver(const std::string& id,
                                 const std::string& parking_id,
                                 double created_time) {
  return {dapp::ParkingDriverId{id},
          parking_id,
          true,
          Time(created_time),
          Time(created_time * 2),
          Time(created_time * 3)};
}

bool ParkingDriverComparator(const dapp::ParkingDriver& lhs,
                             const dapp::ParkingDriver& rhs) {
  return std::tie(lhs.driver_id, lhs.parking_id) <
         std::tie(rhs.driver_id, rhs.parking_id);
}

template <typename ParkingDriversRange>
void Compare(const std::vector<dapp::ParkingDriver>& etalon,
             const ParkingDriversRange& actual) {
  std::vector<dapp::ParkingDriver> etalon_sorted(etalon);
  std::sort(etalon_sorted.begin(), etalon_sorted.end(),
            ParkingDriverComparator);
  std::vector<dapp::ParkingDriver> actual_sorted(std::begin(actual),
                                                 std::end(actual));
  std::sort(actual_sorted.begin(), actual_sorted.end(),
            ParkingDriverComparator);
  ASSERT_EQ(etalon_sorted, actual_sorted);
}

}  // namespace

TEST(ParkingDriversCacheContainer, Empty) {
  caches::ParkingDriversCacheContainer container;
  for ([[maybe_unused]] const auto& driver : container) {
    ASSERT_TRUE(false);
  }
  ASSERT_EQ(container.size(), 0);
}

TEST(ParkingDriversCacheContainer, Insert) {
  std::vector<dapp::ParkingDriver> drivers{
      CreateDriver("driver_id1", "parking_id1", 1),
      CreateDriver("driver_id2", "parking_id2", 2),
      CreateDriver("driver_id3", "parking_id3", 3),
      CreateDriver("driver_id4", "parking_id4", 3),
  };

  auto container = CreateContainer(drivers);
  Compare(drivers, container);

  dapp::ParkingDriver replaced_driver =
      CreateDriver("driver_id5", "parking_id5", 5);
  drivers[1] = replaced_driver;
  container.insert_or_assign(
      {dapp::ParkingDriverId{"driver_id2"}, "parking_id2"},
      std::move(replaced_driver));
  Compare(drivers, container);
}

TEST(ParkingDriversCacheContainer, GetByDriverId) {
  std::unordered_map<std::string, std::vector<dapp::ParkingDriver>>
      drivers_by_driver_id{
          {
              "driver_id0",
              {},
          },
          {
              "driver_id1",
              {
                  CreateDriver("driver_id1", "parking_id1", 1),
              },
          },
          {
              "driver_id2",
              {
                  CreateDriver("driver_id2", "parking_id1", 1),
                  CreateDriver("driver_id2", "parking_id2", 2),
              },
          },
          {
              "driver_id3",
              {
                  CreateDriver("driver_id3", "parking_id1", 3),
                  CreateDriver("driver_id3", "parking_id2", 4),
                  CreateDriver("driver_id3", "parking_id3", 5),
              },
          },
          {
              "driver_id4",
              {
                  CreateDriver("driver_id4", "parking_id1", 6),
                  CreateDriver("driver_id4", "parking_id2", 7),
                  CreateDriver("driver_id4", "parking_id3", 8),
                  CreateDriver("driver_id4", "parking_id4", 9),
              },
          },
      };

  std::vector<dapp::ParkingDriver> drivers;
  for (auto& [id, mapped_drivers] : drivers_by_driver_id) {
    drivers.insert(drivers.end(), mapped_drivers.begin(), mapped_drivers.end());
  }
  const auto container = CreateContainer(drivers);
  for (auto& [id, mapped_drivers] : drivers_by_driver_id) {
    Compare(mapped_drivers, container.GetByDriverId(dapp::ParkingDriverId{id}));
  }
}

TEST(ParkingDriversCacheContainer, GetByParkingId) {
  std::unordered_map<std::string, std::vector<dapp::ParkingDriver>>
      drivers_by_parking_id{

          {
              "parking_id0",
              {},
          },
          {
              "parking_id1",
              {
                  CreateDriver("driver_id1", "parking_id1", 1),
              },
          },
          {
              "parking_id2",
              {
                  CreateDriver("driver_id1", "parking_id2", 1),
                  CreateDriver("driver_id2", "parking_id2", 2),
              },
          },
          {
              "parking_id3",
              {
                  CreateDriver("driver_id1", "parking_id3", 3),
                  CreateDriver("driver_id2", "parking_id3", 4),
                  CreateDriver("driver_id3", "parking_id3", 5),
              },
          },
          {
              "parking_id4",
              {
                  CreateDriver("driver_id1", "parking_id4", 6),
                  CreateDriver("driver_id2", "parking_id4", 7),
                  CreateDriver("driver_id3", "parking_id4", 8),
                  CreateDriver("driver_id4", "parking_id4", 9),
              },
          },
      };
  std::vector<dapp::ParkingDriver> drivers;
  for (auto& [id, mapped_drivers] : drivers_by_parking_id) {
    drivers.insert(drivers.end(), mapped_drivers.begin(), mapped_drivers.end());
  }
  const auto container = CreateContainer(drivers);
  for (auto& [id, mapped_drivers] : drivers_by_parking_id) {
    Compare(mapped_drivers, container.GetByParkingId(id));
  }
}
