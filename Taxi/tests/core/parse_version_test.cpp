#include <userver/utest/utest.hpp>

#include "core/sdk_client.hpp"

namespace plus_plaque::core {

namespace {
void AssertVersion(const SDKVersion& version, int32_t major, int32_t minor,
                   int32_t build) {
  ASSERT_EQ(version.GetVerMajor(), major);
  ASSERT_EQ(version.GetVerMinor(), minor);
  ASSERT_EQ(version.GetVerBuild(), build);
}
}  // namespace

TEST(TestParseVersion, GoodVersions) {
  AssertVersion(ParseVersion("0.0.0"), 0, 0, 0);
  AssertVersion(ParseVersion("1.0.0"), 1, 0, 0);
  AssertVersion(ParseVersion("0.1.0"), 0, 1, 0);
  AssertVersion(ParseVersion("0.0.1"), 0, 0, 1);
  AssertVersion(ParseVersion("1000.0.0"), 1000, 0, 0);
}

TEST(TestParseVersion, BadVersions) {
  const std::vector<std::string> bad_versions{
      "",
      "1",
      "2.",
      "3.0",
      "4.0.",
      "5.0.0.1",
      "a.0.0",
      "7.a.0",
      "8.0.a",
      "only chars",
      "someprefix10.0.0",
      "someprefix11.0.0somesuffix",
      "-1.0.0",
      "1.-50.0",
      "1.0.-30",
  };
  for (const auto& version : bad_versions) {
    ASSERT_THROW(ParseVersion(version), ua_parser::VersionParseError)
        << "Uncaught version - " << version;
  }
}

}  // namespace plus_plaque::core
