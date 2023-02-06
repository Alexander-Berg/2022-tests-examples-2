#include <gtest/gtest.h>

#include <userver/utest/parameter_names.hpp>

#include <utils/hash.hpp>

struct TestParams {
  std::string identity;
  std::string value;
  uint32_t result;

  std::string test_name;

  TestParams(const std::string& identity, const std::string& value,
             uint32_t result)
      : identity(identity), value(value), result(result), test_name(identity) {}
};

class TestCrc32 : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kStandardIdentityValues = {
    {"phone_id", "53903d25b5f273e6a6d342b8", 3756756609},
    {"yandex_uid", "4028849750", 3685604982},
    {"card_id", "044e9aaf146a418e996d9134eacff314", 857054392},
    {"device_id", "11D0D339-1BD2-49A6-B723-D1AEAE0C7873", 3905798889},
};

// This is a check against Crc32 implementation changes.
TEST_P(TestCrc32, FreezeImplementation) {
  const auto param = GetParam();
  const auto input = param.identity + "_" + param.value;
  EXPECT_EQ(utils::hash::Crc32(input), param.result);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestCrc32,
                         testing::ValuesIn(kStandardIdentityValues),
                         ::utest::PrintTestName());
