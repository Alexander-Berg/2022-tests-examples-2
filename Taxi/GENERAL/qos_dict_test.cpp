#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utest/utest.hpp>

#include <clients/codegen/qos_dict.hpp>

namespace clients::codegen {

namespace {

struct QosInfo {
  int attempts{};
  std::chrono::milliseconds timeout_ms{};
};

bool operator==(const QosInfo& lh, const QosInfo& rh) {
  return lh.attempts == rh.attempts && lh.timeout_ms == rh.timeout_ms;
}

using ms = std::chrono::milliseconds;

const std::unordered_map<std::string, QosInfo> kMap = {
    {"/p", QosInfo{1, ms{1}}},
    {"/p@m", {2, ms{2}}},
    {"__default__", {3, ms{3}}},
    {"/o", {4, ms{4}}},
};

}  // namespace

TEST(QosDict, Get) {
  using namespace clients::codegen;

  const dynamic_config::ValueDict<QosInfo> dict("", kMap);

  EXPECT_EQ(GetQosInfoForOperation(dict, "/p", "m"), (QosInfo{2, ms{2}}));
  EXPECT_EQ(GetQosInfoForOperation(dict, "/p", "n"), (QosInfo{1, ms{1}}));
  EXPECT_EQ(GetQosInfoForOperation(dict, "/o", "m"), (QosInfo{4, ms{4}}));
  EXPECT_EQ(GetQosInfoForOperation(dict, "/o", "n"), (QosInfo{4, ms{4}}));

  EXPECT_EQ(GetQosInfoForOperation(dict, "/a", "n"), (QosInfo{3, ms{3}}));
}
}  // namespace clients::codegen
