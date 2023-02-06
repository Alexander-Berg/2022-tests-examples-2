#include <gtest/gtest.h>

#include <userver/dump/common.hpp>
#include <userver/dump/common_containers.hpp>
#include <userver/dump/operations.hpp>
#include <userver/dump/test_helpers.hpp>
#include <userver/utils/datetime.hpp>

#include <caches/models/by_ids/container.hpp>

using caches::models::by_ids::Container;
using DataType = Container::DataType;
using SubDataType = typename DataType::mapped_type;
using ValueType = typename SubDataType::mapped_type;

static_assert(dump::kIsDumpable<ValueType>);
static_assert(dump::kIsDumpable<SubDataType>);
static_assert(dump::kIsDumpable<DataType>);

TEST(ByIdsCacheDump, EmptyData) {
  dump::TestWriteReadCycle(DataType{});
  dump::TestWriteReadCycle(Container{});
}

TEST(ByIdsCacheDump, NonEmptyData) {
  using namespace std::chrono_literals;

  auto now = utils::datetime::Now();
  const DataType data{
      {
          "park_0",
          SubDataType{
              {"driver_0_0", now},
              {"driver_0_1", now - 5s},
          },
      },
      {
          "park_1",
          SubDataType{
              {"driver_1_0", now - 15min},
              {"driver_1_1", now - 10h},
          },
      },
  };
  dump::TestWriteReadCycle(data);
  dump::TestWriteReadCycle(Container(data));
}
