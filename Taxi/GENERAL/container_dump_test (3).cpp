#include <gtest/gtest.h>

#include <userver/dump/common.hpp>
#include <userver/dump/common_containers.hpp>
#include <userver/dump/operations.hpp>
#include <userver/dump/test_helpers.hpp>
#include <userver/utils/datetime.hpp>

#include <caches/models/by_passport_uid/container.hpp>

using caches::models::by_passport_uid::Container;
using DataType = Container::DataType;
using ValueType = typename DataType::mapped_type;

static_assert(dump::kIsDumpable<ValueType>);
static_assert(dump::kIsDumpable<DataType>);

TEST(ByPassportUidCacheDump, EmptyData) {
  dump::TestWriteReadCycle(DataType{});
  dump::TestWriteReadCycle(Container{});
}

TEST(ByPassportUidCacheDump, NonEmptyData) {
  using namespace std::chrono_literals;

  auto now = utils::datetime::Now();
  const DataType data{
      {
          "111222333",
          now,
      },
      {
          "444555666",
          now - 5s,
      },
  };
  dump::TestWriteReadCycle(data);
  dump::TestWriteReadCycle(Container(data));
}
