#include <gtest/gtest.h>

#include <chrono>
#include <optional>
#include <sstream>
#include <string>

#include "api_base/model.hpp"
#include "api_base/utils.hpp"

static const auto date =
    std::chrono::system_clock::time_point(std::chrono::seconds(1234567));
static const formats::bson::Timestamp timestamp{1234567, 12};
static const std::vector<std::string> string_vector = {"aaa", "b", "cccc", ""};
static const std::vector<bool> bool_vector = {true, false};
static const std::vector<std::optional<std::string>> optional_string_vector = {
    std::optional<std::string>("aaa"), std::optional<std::string>(),
    std::optional<std::string>("cc")};

template <class T>
void TestDumpValue(const T& value) {
  std::ostringstream ostr;

  api_over_db::utils::SaveToDump(ostr, value);
  auto dump = ostr.str();

  std::istringstream istr(dump);

  T restored;
  api_over_db::utils::LoadFromDump(istr, restored);

  EXPECT_EQ(value, restored);
}

TEST(ApiOverDbDumper, DumpSingle) {
  TestDumpValue(0l);
  TestDumpValue(12345l);
  TestDumpValue(-12345l);
  TestDumpValue(1538643632889l);
  TestDumpValue(-1538643632889l);
  TestDumpValue(std::string("non-optional str"));
  TestDumpValue(date);
  TestDumpValue(std::make_optional(std::string("optional str")));
  TestDumpValue(std::optional<std::string>());
  TestDumpValue(std::make_optional(date));
  TestDumpValue(std::optional<std::chrono::system_clock::time_point>());
  TestDumpValue(std::vector<long>());
  TestDumpValue(std::vector<long>{1l, 2l, 3l});
  TestDumpValue(std::vector<std::string>());
  TestDumpValue(string_vector);
  TestDumpValue(bool_vector);
  TestDumpValue(std::optional<std::vector<std::string>>());
  TestDumpValue(std::optional<std::vector<std::string>>(string_vector));
  TestDumpValue(optional_string_vector);
}

template <class T>
void LoadAndCheck(std::istream& istr, const T& reference) {
  T restored;
  api_over_db::utils::LoadFromDump(istr, restored);

  EXPECT_EQ(reference, restored);
}

TEST(ApiOverDbDumper, DumpMany) {
  std::ostringstream ostr;

  api_over_db::utils::SaveToDump(ostr, 0l);
  api_over_db::utils::SaveToDump(ostr, 12345l);
  api_over_db::utils::SaveToDump(ostr, -12345l);
  api_over_db::utils::SaveToDump(ostr, 1538643632889l);
  api_over_db::utils::SaveToDump(ostr, -1538643632889l);
  api_over_db::utils::SaveToDump(ostr, std::string("non-optional str"));
  api_over_db::utils::SaveToDump(ostr, date);
  api_over_db::utils::SaveToDump(
      ostr, std::make_optional(std::string("optional str")));
  api_over_db::utils::SaveToDump(ostr, std::optional<std::string>());
  api_over_db::utils::SaveToDump(ostr, std::make_optional(date));
  api_over_db::utils::SaveToDump(
      ostr, std::optional<std::chrono::system_clock::time_point>());
  api_over_db::utils::SaveToDump(ostr, timestamp);
  api_over_db::utils::SaveToDump(ostr, std::vector<long>());
  api_over_db::utils::SaveToDump(ostr, std::vector<long>{1l, 2l, 3l});
  api_over_db::utils::SaveToDump(ostr, std::vector<std::string>());
  api_over_db::utils::SaveToDump(ostr, string_vector);
  api_over_db::utils::SaveToDump(ostr, bool_vector);
  api_over_db::utils::SaveToDump(ostr,
                                 std::optional<std::vector<std::string>>());
  api_over_db::utils::SaveToDump(
      ostr, std::optional<std::vector<std::string>>(string_vector));
  api_over_db::utils::SaveToDump(ostr, optional_string_vector);

  std::istringstream istr(ostr.str());

  LoadAndCheck(istr, 0l);
  LoadAndCheck(istr, 12345l);
  LoadAndCheck(istr, -12345l);
  LoadAndCheck(istr, 1538643632889l);
  LoadAndCheck(istr, -1538643632889l);
  LoadAndCheck(istr, std::string("non-optional str"));
  LoadAndCheck(istr, date);
  LoadAndCheck(istr, std::make_optional(std::string("optional str")));
  LoadAndCheck(istr, std::optional<std::string>());
  LoadAndCheck(istr, std::make_optional(date));
  LoadAndCheck(istr, std::optional<std::chrono::system_clock::time_point>());
  LoadAndCheck(istr, timestamp);
  LoadAndCheck(istr, std::vector<long>());
  LoadAndCheck(istr, std::vector<long>{1l, 2l, 3l});
  LoadAndCheck(istr, std::vector<std::string>());
  LoadAndCheck(istr, string_vector);
  LoadAndCheck(istr, bool_vector);
  LoadAndCheck(istr, std::optional<std::vector<std::string>>());
  LoadAndCheck(istr, std::optional<std::vector<std::string>>(string_vector));
  LoadAndCheck(istr, optional_string_vector);
}
