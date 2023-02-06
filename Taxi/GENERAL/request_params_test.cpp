#include "request_params.hpp"

#include <gtest/gtest.h>

namespace {
using Version = ua_parser::ApplicationVersion;

std::string VersionOrEmpty(const std::optional<Version>& ver) {
  if (ver.has_value()) {
    return ver->ToString();
  }
  return "";
}

}  // namespace

TEST(RequestParams, ParseVersion) {
  struct TestCase {
    std::string x_app_version;
    std::optional<Version> expected;
  };

  std::vector<TestCase> tt = {
      TestCase{"1.0", Version(1, 0, 0)},
      TestCase{"2.2.1", Version(2, 2, 1)},
      TestCase{"", std::nullopt},
      TestCase{"invalid-version-v2.2", std::nullopt},
      TestCase{" 2.2.2", Version(2, 2, 2)},
  };

  for (const auto& tc : tt) {
    auto result =
        eats_layout_constructor::models::ParseVersion(tc.x_app_version);

    EXPECT_EQ(result, tc.expected) << "expected " << VersionOrEmpty(tc.expected)
                                   << ", got " << VersionOrEmpty(result);
  }
}
