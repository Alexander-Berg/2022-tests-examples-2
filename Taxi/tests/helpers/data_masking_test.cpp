#include <helpers/data_masking.hpp>
#include <userver/utest/utest.hpp>

namespace eats_restapp_communications::helpers {

struct DataMaskingParams {
  const formats::json::Value data;
  std::set<sensitive_data_masking::JsonPath> expected_result;
};

struct DataMaskingTest : public ::testing::TestWithParam<DataMaskingParams> {};

const std::vector<DataMaskingParams> kDataMaskingParamsData{
    {formats::json::FromString(R"(
            {}
        )"),
     {}},
    {formats::json::FromString(R"(
            []
        )"),
     {}},
    {formats::json::FromString(R"(
            {
                "no_password": []
            }
        )"),
     {}},
    {formats::json::FromString(R"(
            {
                "no_password": {}
            }
        )"),
     {}},
    {formats::json::FromString(R"(
            {"no_password": "password"}
        )"),
     {}},
    {formats::json::FromString(R"(
            {"password": "password"}
        )"),
     {{"password"}}},
    {formats::json::FromString(R"(
            {"password": {"password1": 1, "password2": 2, "password": 3}}
        )"),
     {{"password"}}},
    {formats::json::FromString(R"(
            {"password": [1, 2, 3]}
        )"),
     {{"password"}}},
    {formats::json::FromString(R"(
            {
                "data": {
                    "common_email": "email",
                    "password": "password",
                    "users": [
                        {
                            "email": "email1",
                            "password": "password1"
                        },
                        {
                            "email": "email2",
                            "password": "password2"
                        },
                        {
                            "no_email": "email3",
                            "no_password": "password3"
                        }
                    ],
                    "all_passwords": ["password", "password1", "password2", "password3"]
                }
            }
        )"),
     {{"data", "password"}, {"data", "users", "password"}}},
    {formats::json::FromString(R"(
            {
                "data": {
                    "common_email": "email",
                    "password": "password",
                    "users": [
                        {
                            "restaurant": [
                                {
                                    "email": "email1",
                                    "password": "password1"
                                },
                                {
                                    "email": "email2"
                                },
                                {
                                    "password": "password3"
                                },
                                {
                                    "no_password": "no_password"
                                }
                            ],
                            "person_data": {
                                "email": "email",
                                "password": "password"
                            },
                            "number": 1
                        },
                        {
                            "email": "email2",
                            "password": "password2"
                        }
                    ],
                    "all_passwords": ["password", "password1", "password2", "password3"]
                }
            }
        )"),
     {{"data", "password"},
      {"data", "users", "password"},
      {"data", "users", "restaurant", "password"},
      {"data", "users", "person_data", "password"}}}};

INSTANTIATE_TEST_SUITE_P(DataMaskingParams, DataMaskingTest,
                         ::testing::ValuesIn(kDataMaskingParamsData));

TEST_P(DataMaskingTest, should_make_json_path_to_field) {
  auto param = GetParam();
  std::set<sensitive_data_masking::JsonPath> result;
  MakePathsToMask(param.data, result);
  ASSERT_EQ(result, param.expected_result);
}

}  // namespace eats_restapp_communications::helpers
