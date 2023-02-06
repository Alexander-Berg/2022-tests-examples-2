#include <userver/utest/utest.hpp>

#include "ab/kwargs_builder.hpp"

namespace {

void CheckVersion(const char* input, const char* expected_output) {
  ASSERT_EQ(
      eats_launch::ab::KwargsBuilderWithLog::FixVersion(std::string(input)),
      std::string(expected_output));
}

}  // namespace

TEST(FixVersion, FullVersion2) { CheckVersion("99.99.99", "99.99.99"); }

TEST(FixVersion, FullVersion1) { CheckVersion("1.1.1", "1.1.1"); }

TEST(FixVersion, LongVersion) { CheckVersion("1.1.1.1", "1.1.1"); }

TEST(FixVersion, PartialVersion2Dot) {
  // The former ab service does not fix such versions.
  CheckVersion("1.1.", "1.1.");
}

TEST(FixVersion, PartialVersion2) { CheckVersion("1.1", "1.1.0"); }

TEST(FixVersion, PartialVersion1Dot) {
  // The former ab service does not fix such versions.
  CheckVersion("1.", "1..0");
}

TEST(FixVersion, PartialVersion1) { CheckVersion("1", "1.0.0"); }

TEST(FixVersion, EmptyVersion) { CheckVersion("", "0.0.0"); }
