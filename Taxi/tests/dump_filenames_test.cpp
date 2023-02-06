#include <gtest/gtest.h>

#include <chrono>
#include <ios>
#include <set>

#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <api_base/cache_dumper.hpp>

using TimePoint = std::chrono::system_clock::time_point;
using ParsedDumpFilename = api_over_db::ParsedDumpFilename;
using DumpContext = api_over_db::DumpContext;
const auto& kDumpFilenameDateFormat = api_over_db::kDumpFilenameDateFormat;

namespace api_over_db {

std::ostream& operator<<(std::ostream& ostr, const ParsedDumpFilename& value) {
  ostr << "{" << value.filename << ", "
       << ::utils::datetime::Timestring(value.creation_time, "UTC",
                                        kDumpFilenameDateFormat)
       << ", " << value.version << "}";
  return ostr;
}

}  // namespace api_over_db

std::ostream& operator<<(std::ostream& ostr,
                         const std::set<ParsedDumpFilename>& value) {
  ostr << "{";
  for (const auto& elem : value) {
    ostr << elem << ",";
  }
  return ostr;
}

const TimePoint kSampleTimePoint1 = ::utils::datetime::Stringtime(
    "2015-03-22T09-00-00", "UTC", kDumpFilenameDateFormat);
const TimePoint kSampleTimePoint2 = ::utils::datetime::Stringtime(
    "2015-03-23T12-00-00", "UTC", kDumpFilenameDateFormat);
const TimePoint kSampleTimePoint3 = ::utils::datetime::Stringtime(
    "2015-03-23T14-00-00", "UTC", kDumpFilenameDateFormat);
const TimePoint kSampleTimePoint4 = ::utils::datetime::Stringtime(
    "2015-03-23T16-00-00", "UTC", kDumpFilenameDateFormat);

const std::string kTestPrefix = "dump-test";

DumpContext kTestDumpContext1{"dump-test", "1"};
DumpContext kTestDumpContext2{"dump-test", "2"};

ParsedDumpFilename MakeParsedDumpFilename(const std::string& prefix,
                                          TimePoint time,
                                          const std::string& version) {
  return ParsedDumpFilename{
      prefix + "-date-" +
          ::utils::datetime::Timestring(
              time, "UTC", kDumpFilenameDateFormat + "-version-" + version),
      time, version};
}

TEST(ApiOverDbDumpFilenames, GenDumpFilenameTest) {
  ::utils::datetime::MockNowSet(kSampleTimePoint1);
  const auto filename = GenDumpFilename(kTestDumpContext2);
  const std::string expected = "dump-test-date-2015-03-22T09-00-00-version-2";
  EXPECT_EQ(expected, filename);
  ::utils::datetime::MockNowUnset();
}

TEST(ApiOverDbDumpFilenames, ParseDumpFilenameTest) {
  auto parsed = ParseDumpFilename(
      "dump-test-date-2015-03-22T09-00-00-version-2", kTestDumpContext1);
  ASSERT_TRUE(bool(parsed));
  ParsedDumpFilename expected =
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint1, "2");
  EXPECT_EQ(expected, *parsed);

  auto parsed2 = ParseDumpFilename(
      "dump-test-2-date-2015-03-22T09-00-00-version-2", kTestDumpContext1);
  EXPECT_FALSE(bool(parsed2));

  auto parsed3 = ParseDumpFilename("config.json", kTestDumpContext1);
  EXPECT_FALSE(bool(parsed3));
}

std::set<std::string> MakeSet(const std::vector<std::string>& v) {
  return {v.begin(), v.end()};
}

TEST(ApiOverDbDumpFilenames, GetMatchedFilesTest) {
  std::vector<std::string> filenames{
      "dump-test-date-2015-03-22T09-00-00-version-1",
      "dump-test-date-2015-03-23T12-00-00-version-2",
      "dump-test-date-2015-03-23T14-00-00-version-3",
      "dump-test-2-date-2015-03-23T10-00-00-version-2"};

  std::set<ParsedDumpFilename> expected_same_version{
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint2, "2")};

  EXPECT_EQ(expected_same_version,
            GetMatchedFiles(filenames, kTestDumpContext2, true));

  std::set<ParsedDumpFilename> expected_all_versions{
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint1, "1"),
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint2, "2"),
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint3, "3")};

  EXPECT_EQ(expected_all_versions,
            GetMatchedFiles(filenames, kTestDumpContext2, false));
}

TEST(ApiOverDbDumpFilenames, GetFilesToRemoveTest) {
  ::utils::datetime::MockNowSet(kSampleTimePoint4);
  std::set<ParsedDumpFilename> matched_files{
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint1, "1"),
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint2, "2"),
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint3, "3"),
      MakeParsedDumpFilename(kTestPrefix, kSampleTimePoint4, "2")};
  std::set<std::string> expected_with_ttl = {
      "dump-test-date-2015-03-22T09-00-00-version-1",
      "dump-test-date-2015-03-23T12-00-00-version-2"};
  auto to_remove_with_ttl =
      GetFilesToRemove(matched_files, 1, 1, kTestDumpContext2);
  EXPECT_EQ(expected_with_ttl, to_remove_with_ttl);

  std::set<std::string> expected_no_ttl = {
      "dump-test-date-2015-03-23T12-00-00-version-2"};
  auto to_remove_no_ttl =
      GetFilesToRemove(matched_files, 1, -1, kTestDumpContext2);
  EXPECT_EQ(expected_no_ttl, to_remove_no_ttl);
  ::utils::datetime::MockNowUnset();
}
