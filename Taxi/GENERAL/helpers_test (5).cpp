#include <gtest/gtest.h>

#include <array>

#include <userver/formats/json.hpp>

#include "helpers.hpp"

// This is for test printing. gtest require function PrintTo in same namespace
// as value. Maybe UB
namespace std {

void PrintTo(std::chrono::system_clock::time_point value,
             std::ostream* stream) {
  *stream << value.time_since_epoch().count();
}

void PrintTo(std::optional<std::chrono::system_clock::time_point> value,
             std::ostream* stream) {
  if (!value) {
    *stream << "std::nullopt";
  } else {
    PrintTo(*value, stream);
  }
}

}  // namespace std

namespace jams_closures::helpers {

inline formats::json::Value operator"" _json(const char* str, size_t len) {
  return formats::json::FromString(std::string_view(str, len));
}

auto FromSeconds(size_t value) {
  const std::chrono::seconds seconds{value};
  return std::chrono::system_clock::time_point{seconds};
}

struct FetchDateParam {
  formats::json::Value meta_data;
  std::optional<std::chrono::system_clock::time_point> expected_date;
};

auto MakeFetchDateData() {
  return std::array{
      // clang-format off
    FetchDateParam{
      "{}"_json,
      std::nullopt
    },
    FetchDateParam{
      R"({
        "jams_timestamp": 1605168270
      })"_json,
      FromSeconds(1605168270ull)
    },
    FetchDateParam{
      R"({
        "jams_date": "2019-10-08T11:10:07"
      })"_json,
      FromSeconds(1570533007ull)
    },
    FetchDateParam{
      R"({
        "jams_date": "2019-10-08T11:10:07.0000"
      })"_json,
      FromSeconds(1570533007ull)
    },
    FetchDateParam{
      R"({
        "jams_date": "2019-10-08T11:10:07+00:00"
      })"_json,
      FromSeconds(1570533007ull)
    },
    FetchDateParam{
      R"({
        "jams_date": "2019-10-08T11:10:07.0000+00:00"
      })"_json,
      FromSeconds(1570533007ull)
    },
    FetchDateParam{
      R"({
        "jams_date": "some_not_date_string"
      })"_json,
      std::nullopt
    }
      // clang-format on
  };
}

struct TestTryFetchDate : public ::testing::TestWithParam<FetchDateParam> {};

TEST_P(TestTryFetchDate, Simple) {
  const std::string timestamp_name{"jams_timestamp"};
  const std::string date_name{"jams_date"};
  const auto result =
      TryFetchDate(GetParam().meta_data, timestamp_name, date_name);
  ASSERT_EQ(result, GetParam().expected_date);
}

INSTANTIATE_TEST_SUITE_P(TestTryFetchDate, TestTryFetchDate,
                         ::testing::ValuesIn(MakeFetchDateData()));

struct FetchCustomDateParam {
  formats::json::Value meta_data;
};

auto MakeFetchCustomDateData() {
  return std::array{
      // clang-format off
    FetchCustomDateParam{
      R"({
        "jams_timestamp": 1584144000,
        "upload_timestamp": 1584234000,
        "download_timestamp": 1584324000
      })"_json
    },
    FetchCustomDateParam{
      R"({
        "jams_date": "2020-03-14T00:00:00+00:00",
        "upload_date": "2020-03-15T01:00:00",
        "download_date": "2020-03-16T02:00:00.0000"
      })"_json
    }
      // clang-format on
  };
}

struct TestTryFetchCustomDate
    : public ::testing::TestWithParam<FetchCustomDateParam> {};

TEST_P(TestTryFetchCustomDate, Simple) {
  const auto jams_date = TryFetchJamsDate(GetParam().meta_data);
  ASSERT_TRUE(jams_date);
  ASSERT_EQ(*jams_date, FromSeconds(1584144000));

  const auto upload_date = TryFetchUploadDate(GetParam().meta_data);
  ASSERT_TRUE(upload_date);
  ASSERT_EQ(*upload_date, FromSeconds(1584234000));

  const auto download_date = TryFetchDownloadDate(GetParam().meta_data);
  ASSERT_TRUE(download_date);
  ASSERT_EQ(*download_date, FromSeconds(1584324000));
}

INSTANTIATE_TEST_SUITE_P(TestTryFetchCustomDate, TestTryFetchCustomDate,
                         ::testing::ValuesIn(MakeFetchCustomDateData()));

}  // namespace jams_closures::helpers
