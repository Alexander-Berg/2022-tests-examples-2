#include <gtest/gtest.h>

#include <userver/dump/common.hpp>
#include <userver/dump/common_containers.hpp>
#include <userver/dump/operations.hpp>
#include <userver/dump/test_helpers.hpp>

#include <caches/models/affiliations/container.hpp>

using caches::models::affiliations::Container;
using DataType = Container::DataType;
using SubDataType = typename DataType::mapped_type;
using ValueType = typename SubDataType::value_type;

static_assert(dump::kIsDumpable<ValueType>);
static_assert(dump::kIsDumpable<SubDataType>);
static_assert(dump::kIsDumpable<DataType>);
static_assert(dump::kIsDumpable<Container>);

TEST(AffiliationsDump, EmptyData) { dump::TestWriteReadCycle(Container{}); }

TEST(AffiliationsDump, NonEmptyData) {
  for (const auto& cursor : std::vector<std::optional<std::string>>{
           "shortstring",
           "very long string to allocate on heap",
           std::nullopt,
       }) {
    const caches::models::affiliations::Container container{
        {
            {"park_0", SubDataType{"driver_0_0", "driver_0_1"}},
            {"park_1", SubDataType{"driver_1_0", "driver_1_1"}},
            {"park_2", SubDataType{}},
        },
        cursor,
    };
    dump::TestWriteReadCycle(container);
  }
}
