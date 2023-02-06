#include <userver/utest/utest.hpp>

#include <array>
#include <internal/yaga_hash.hpp>
#include <variant>

// TODO: this file is not used, maybe delete it

namespace {

using DriverId = driver_id::DriverDbidUndscrUuid;
using DriverIdKey = yaga::internal::DriverIdKey;

using AnyDriverId = std::variant<DriverId, DriverIdKey>;

DriverId MakeDriverId(const char* dbid, const char* uuid) {
  using driver_id::DriverDbidView;
  using driver_id::DriverUuidView;
  return {DriverDbidView{dbid}, DriverUuidView{uuid}};
}

DriverIdKey MakeDriverIdKey(const char* dbid, const char* uuid) {
  using driver_id::DriverDbid;
  using driver_id::DriverUuid;
  return {DriverDbid{dbid}, DriverUuid{uuid}};
}

uint64_t CalculateHash(const AnyDriverId& any_driver_id) {
  auto visitor = [](const auto& driver_id) {
    return yaga::YagaHash(driver_id);
  };
  return std::visit(visitor, any_driver_id);
}

struct TestParam {
  TestParam(AnyDriverId driver_id, uint64_t hash)
      : driver_id(std::move(driver_id)), hash(hash) {}
  AnyDriverId driver_id;
  uint64_t hash;
};

auto MakeRawTestData() {
  struct RawTestParams {
    const char* dbid;
    const char* uuid;
    uint64_t hash;
  };
  // clang-format off
  return std::array{
    RawTestParams{
      "812ef461837d45ac8c714f0b9a94d2c9",
      "c5f231580f701eaed75791392e561eb5",
      7878445591185401914ull
    },
    RawTestParams{
      "cd7b9e461a60472e86dacb5d08532ccb",
      "77d5623a34bb9c8a3639a0d7e92ca0f2",
      3096957691686750323ull
    },
    RawTestParams{
      "f1cbdd78d7054a9984e6e307b9d97e32",
      "8bc858adefd417d0fef4d1d43cc8e192",
      4549539261131143685ull
    },
  };
  // clang-format on
}

std::vector<TestParam> MakeTestData() {
  auto raw_test_data = MakeRawTestData();
  std::vector<TestParam> result;
  result.reserve(raw_test_data.size() * 2);
  for (const auto& element : raw_test_data) {
    result.emplace_back(MakeDriverId(element.dbid, element.uuid), element.hash);
    result.emplace_back(MakeDriverIdKey(element.dbid, element.uuid),
                        element.hash);
  }
  return result;
};

struct TestYagaHash : public ::testing::TestWithParam<TestParam> {};

TEST_P(TestYagaHash, SimpleTest) {
  const auto& test_param = GetParam();
  ASSERT_EQ(test_param.hash, CalculateHash(test_param.driver_id));
}

INSTANTIATE_TEST_SUITE_P(TestYagaHash, TestYagaHash,
                         ::testing::ValuesIn(std::vector<TestParam>{
                             MakeTestData()}));

}  // namespace
