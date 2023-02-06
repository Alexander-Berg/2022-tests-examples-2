#include <gtest/gtest.h>

#include <logging/log_extra.hpp>
#include <models/parks/driver_profiles/search_request_builder.hpp>
#include <models/parks/driver_profiles/search_request_utils.hpp>

namespace models {
namespace parks {
namespace driver_profiles {

SearchRequest TestRequest() {
  return SearchRequest{{"park_abc"},
                       {"driver_abc"},
                       {"car_id"},
                       {"rule_id"},
                       {"+79104607457"},
                       {"platform_uid_27"},
                       {"ABCD123456"},
                       {"ABCD123456"},
                       {"Тодуа"},
                       {"work"},
                       {"account_abc"},
                       {"id"},
                       {"id", "last_name"},
                       {"balance"},
                       123,
                       777};
}

SearchRequest TruncateFields(SearchRequest request) {
  request.park_fields.clear();
  request.driver_fields.clear();
  request.account_fields.clear();
  return request;
}

std::set<std::string> MakeSet(const SearchFields& fields) {
  return std::set<std::string>(fields.begin(), fields.end());
}

void AssertEq(const SearchRequest& expected, const SearchRequest& actual) {
  ASSERT_EQ(expected.park_id, actual.park_id);
  ASSERT_EQ(expected.driver_id, actual.driver_id);
  ASSERT_EQ(expected.driver_car_id, actual.driver_car_id);
  ASSERT_EQ(expected.driver_rule_id, actual.driver_rule_id);
  ASSERT_EQ(expected.driver_phone, actual.driver_phone);
  ASSERT_EQ(expected.driver_platform_uid, actual.driver_platform_uid);
  ASSERT_EQ(expected.driver_license, actual.driver_license);
  ASSERT_EQ(expected.driver_license_normalized,
            actual.driver_license_normalized);
  ASSERT_EQ(expected.driver_last_name, actual.driver_last_name);
  ASSERT_EQ(expected.driver_work_status, actual.driver_work_status);
  ASSERT_EQ(expected.account_id, actual.account_id);
  ASSERT_EQ(MakeSet(expected.park_fields), MakeSet(actual.park_fields));
  ASSERT_EQ(MakeSet(expected.driver_fields), MakeSet(actual.driver_fields));
  ASSERT_EQ(MakeSet(expected.account_fields), MakeSet(actual.account_fields));
  ASSERT_EQ(expected.limit, actual.limit);
  ASSERT_EQ(expected.offset, actual.offset);
}

TEST(SearchRequest, Builder) {
  const auto expected = TestRequest();
  const auto actual =
      SearchRequestBuilder()
          .SetAccountFields(expected.account_fields)
          .SetAccountId(expected.account_id.front())
          .SetDriverFields(expected.driver_fields)
          .SetDriverId(expected.driver_id.front())
          .SetDriverCarId(expected.driver_car_id.front())
          .SetDriverRuleId(expected.driver_rule_id.front())
          .SetDriverPhone(expected.driver_phone.front())
          .SetDriverPlatformUid(expected.driver_platform_uid.front())
          .SetDriverLicense(expected.driver_license.front())
          .SetDriverLicenseNormalized(
              expected.driver_license_normalized.front())
          .SetDriverLastName(expected.driver_last_name.front())
          .SetDriverWorkStatus(expected.driver_work_status.front())
          .SetParkFields(expected.park_fields)
          .SetParkId(expected.park_id.front())
          .SetLimit(123)
          .SetOffset(777)
          .Build();
  AssertEq(expected, actual);
}

TEST(SearchRequest, ParseWithFields) {
  const auto expected = TestRequest();
  const auto& json_text = DumpSearchRequest(expected);
  LogExtra log_extra;
  const auto actual = ParseSearchRequest(json_text, log_extra);
  AssertEq(expected, actual);
}

TEST(SearchRequest, ParseWithoutFields) {
  const auto expected = TestRequest();
  const auto& json_text = DumpSearchRequest(expected);
  LogExtra log_extra;
  const auto actual = ParseSearchRequest(json_text, log_extra, false);
  AssertEq(TruncateFields(expected), actual);
}

}  // namespace driver_profiles
}  // namespace parks
}  // namespace models
