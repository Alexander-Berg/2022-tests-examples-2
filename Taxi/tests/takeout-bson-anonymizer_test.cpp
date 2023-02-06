#include <fmt/core.h>
#include <gtest/gtest.h>
#include <takeout-bson-anonymizer/takeout-bson-anonymizer.hpp>
#include <userver/formats/bson/value_builder.hpp>
#include <userver/formats/json.hpp>
#include "userver/formats/bson/binary.hpp"
#include "userver/formats/bson/serialize.hpp"

namespace {

using takeout_bson_anonymizer::AnonymizeGroup;
using takeout_bson_anonymizer::AnonymizeKind;
using takeout_bson_anonymizer::FieldMetadata;

}  // namespace

TEST(JsonPath, DFS) {
  static const auto source_doc = formats::bson::FromJsonString(R"(
    {
        "field": [
          {
            "subfield_strings": [
              "0_0",
              "0_1"
            ],
            "not_accounted_field": "value"
          },
          {
            "subfield_dicts_1": [
              {
                "value": "1_0",
                "not_accounted_field": "value"
              },
              {
                "value": "1_1"
              }
            ],
            "not_accounted_field": "value"
          },
          {
            "subfield_dicts_2": [
              { "value": "2_0" },
              { "value": "2_1" }
            ],
            "not_accounted_field": "value"
          }
        ],
        "not_accounted_field": "value"
    }
  )");
  static const std::vector<FieldMetadata> expected_fields = {
      {
          "field.0.subfield_strings.0",
          formats::bson::ValueBuilder("0_0").ExtractValue(),
          formats::bson::ValueBuilder("").ExtractValue(),
      },
      {
          "field.0.subfield_strings.1",
          formats::bson::ValueBuilder("0_1").ExtractValue(),
          formats::bson::ValueBuilder("").ExtractValue(),
      },
      {
          "field.1.subfield_dicts_1.0.value",
          formats::bson::ValueBuilder("1_0").ExtractValue(),
          formats::bson::ValueBuilder("").ExtractValue(),
      },
      {
          "field.1.subfield_dicts_1.1.value",
          formats::bson::ValueBuilder("1_1").ExtractValue(),
          formats::bson::ValueBuilder("").ExtractValue(),
      },
      {
          "field.2.subfield_dicts_2.0",
          formats::bson::FromJsonString(R"({ "value": "2_0" })"),
          formats::bson::FromJsonString(R"({})"),
      },
      {
          "field.2.subfield_dicts_2.1",
          formats::bson::FromJsonString(R"({ "value": "2_1" })"),
          formats::bson::FromJsonString(R"({})"),
      },
  };
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kEmptyString, {"field.*.subfield_strings.*"}},
      {AnonymizeKind::kEmptyString, {"field.*.subfield_dicts_1.*.value"}},
      {AnonymizeKind::kEmptyDict, {"field.*.subfield_dicts_2.*"}},
  };
  auto fields = BuildAnonymizedFields(source_doc, kAnonymizeRules);
  std::sort(fields.begin(), fields.end(),
            [](const FieldMetadata& a, const FieldMetadata& b) {
              return a.json_path < b.json_path;
            });
  ASSERT_EQ(fields.size(), expected_fields.size());
  for (size_t i = 0; i < fields.size(); ++i) {
    const auto& left = fields[i];
    const auto& right = expected_fields[i];
    ASSERT_EQ(left.json_path, right.json_path);
    ASSERT_EQ(left.original_value, right.original_value);
    ASSERT_EQ(left.anonymized_value, right.anonymized_value);
  }
}

TEST(SingleKind, EmptyString) {
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kEmptyString, {"field"}},
  };
  formats::bson::ValueBuilder builder;
  builder["field"] = "some-value";
  auto fields = BuildAnonymizedFields(builder.ExtractValue(), kAnonymizeRules);
  ASSERT_EQ(fields.size(), 1);
  const auto& field = fields[0];
  ASSERT_TRUE(field.anonymized_value.IsString());
  ASSERT_EQ(field.anonymized_value.As<std::string>(), "");
}

TEST(SingleKind, EmptyDict) {
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kEmptyDict, {"field"}},
  };
  formats::bson::ValueBuilder builder;
  auto dict_builder = builder["field"];
  dict_builder["key"] = "value";
  auto fields = BuildAnonymizedFields(builder.ExtractValue(), kAnonymizeRules);
  ASSERT_EQ(fields.size(), 1);
  const auto& field = fields[0];
  ASSERT_TRUE(field.anonymized_value.IsDocument());
  ASSERT_EQ(field.anonymized_value.begin(), field.anonymized_value.end());
}

TEST(SingleKind, PassportUid) {
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kPassportUid, {"field_1", "field_2"}},
  };
  formats::bson::ValueBuilder builder;
  builder["field_1"] = "4086105037";
  builder["field_2"] = "4086105037";
  auto fields = BuildAnonymizedFields(builder.ExtractValue(), kAnonymizeRules);
  ASSERT_EQ(fields.size(), 2);
  const auto& field = fields[0];
  ASSERT_TRUE(field.anonymized_value.IsString());
  const auto str_val = field.anonymized_value.As<std::string>();
  ASSERT_EQ(str_val[0], '-');
  ASSERT_EQ(str_val.length(), 11);
  ASSERT_EQ(str_val, fields[1].anonymized_value.As<std::string>());
}

TEST(SingleKind, HexUid) {
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kHexUuid, {"field"}},
  };
  formats::bson::ValueBuilder builder;
  builder["field"] = "561166a2b2ec44b09e20d79a8470f902";
  auto fields = BuildAnonymizedFields(builder.ExtractValue(), kAnonymizeRules);
  ASSERT_EQ(fields.size(), 1);
  const auto& field = fields[0];
  ASSERT_TRUE(field.anonymized_value.IsString());
  const auto str_val = field.anonymized_value.As<std::string>();
  ASSERT_EQ(str_val.length(), 32);
  ASSERT_NE(str_val, field.original_value.As<std::string>());
}

TEST(SingleKind, BsonOid) {
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kBsonOid, {"field"}},
  };
  formats::bson::ValueBuilder builder;
  builder["field"] = formats::bson::Oid();
  auto fields = BuildAnonymizedFields(builder.ExtractValue(), kAnonymizeRules);
  ASSERT_EQ(fields.size(), 1);
  const auto& field = fields[0];
  ASSERT_TRUE(field.anonymized_value.IsOid());
  const auto str_val = field.anonymized_value.ConvertTo<std::string>();
  ASSERT_EQ(str_val.length(), 24);
  ASSERT_NE(str_val, field.original_value.ConvertTo<std::string>());
}

TEST(SingleKind, IpAddress) {
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kIpAdress,
       {"invalid_ip_1", "invalid_ip_2", "ip_v4", "ip_v6"}},
  };
  formats::bson::ValueBuilder builder;
  builder["invalid_ip_1"] = "qwerty";
  builder["invalid_ip_2"] = formats::bson::ValueBuilder("sub_dict");
  builder["ip_v4"] = "127.0.0.1";
  builder["ip_v6"] = "2a02:6b8:b010:7047::3";
  auto fields = BuildAnonymizedFields(builder.ExtractValue(), kAnonymizeRules);
  std::sort(fields.begin(), fields.end(),
            [](const FieldMetadata& a, const FieldMetadata& b) {
              return a.json_path < b.json_path;
            });
  ASSERT_EQ(fields.size(), 4);
  std::vector<std::string> anonymized_values;
  for (const auto& field : fields) {
    anonymized_values.emplace_back(
        field.anonymized_value.ConvertTo<std::string>());
  }
  ASSERT_EQ(anonymized_values, std::vector<std::string>({
                                   "",
                                   "",
                                   "127.0.0.0",
                                   "2a02:6b8:b010:7047::0",
                               }));
}

TEST(SingleKind, GeopointAsArray) {
  static const auto source_doc = formats::bson::FromJsonString(R"(
    {
        "geopoint": [
          37.550863,
          55.664921
        ],
        "invalid_number_of_values_1": [
          1
        ],
        "invalid_number_of_values_2": [
          1,
          2,
          3
        ],
        "not_array": {},
        "not_numbers_in_array": [
          "not_a_number",
          "not_a_number"
        ]
    }
  )");
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kGeopointAsArray,
       {
           "geopoint",
           "invalid_number_of_values_1",
           "invalid_number_of_values_2",
           "not_array",
           "not_numbers_in_array",
       }},
  };
  auto fields = BuildAnonymizedFields(source_doc, kAnonymizeRules);
  std::sort(fields.begin(), fields.end(),
            [](const FieldMetadata& a, const FieldMetadata& b) {
              return a.json_path < b.json_path;
            });
  std::vector<formats::bson::Value> anonymized_values;
  for (const auto& field : fields) {
    anonymized_values.emplace_back(field.anonymized_value);
  }
  static const auto default_value =
      formats::bson::ArrayFromJsonString(R"([0, 0])");
  std::vector<formats::bson::Value> expected_values{
      formats::bson::ArrayFromJsonString(R"([37.551, 55.665])"),
      default_value,
      default_value,
      default_value,
      default_value,
  };
  ASSERT_EQ(anonymized_values.size(), expected_values.size());

  for (size_t i = 0; i < anonymized_values.size(); ++i) {
    const auto& anonymized_value = anonymized_values[i];
    ASSERT_TRUE(anonymized_value.IsArray());
    std::vector<double> anonymized_numbers;
    for (const auto& num : anonymized_value) {
      anonymized_numbers.push_back(num.As<double>());
    }

    const auto& expected_value = expected_values[i];
    ASSERT_TRUE(expected_value.IsArray());
    std::vector<double> expected_numbers;
    for (const auto& num : expected_value) {
      expected_numbers.push_back(num.As<double>());
    }

    ASSERT_EQ(anonymized_numbers, expected_numbers);
  }

  ASSERT_EQ(anonymized_values, expected_values);
}

TEST(SingleKind, GeopointAsObject) {
  static const auto source_doc = formats::bson::FromJsonString(R"(
    {
        "geopoint_as_object": {
          "lat": 55.658126,
          "lon": 37.541448
        },
        "missing_item_1": {
          "lat": 55.658126
        },
        "missing_item_2": {
          "lon": 37.541448
        },
        "not_object": [],
        "not_numbers_in_object": {
          "lat": "55.658126",
          "lon": "37.541448"
        }
    }
  )");
  static const std::vector<AnonymizeGroup> kAnonymizeRules{
      {AnonymizeKind::kGeopointAsObject,
       {
           "geopoint_as_object",
           "missing_item_1",
           "missing_item_2",
           "not_object",
           "not_numbers_in_object",
       }},
  };
  auto fields = BuildAnonymizedFields(source_doc, kAnonymizeRules);
  std::sort(fields.begin(), fields.end(),
            [](const FieldMetadata& a, const FieldMetadata& b) {
              return a.json_path < b.json_path;
            });
  std::vector<formats::bson::Value> anonymized_values;
  for (const auto& field : fields) {
    anonymized_values.emplace_back(field.anonymized_value);
  }
  static const auto default_value =
      formats::bson::FromJsonString(R"({ "lat": 0, "lon": 0 })");
  std::vector<formats::bson::Value> expected_values{
      formats::bson::FromJsonString(R"({ "lat": 55.658, "lon": 37.541 })"),
      default_value,
      default_value,
      default_value,
      default_value,
  };
  ASSERT_EQ(anonymized_values.size(), expected_values.size());
  struct GeoPoint {
    double lat;
    double lon;
  };
  for (size_t i = 0; i < anonymized_values.size(); ++i) {
    const auto& anonymized_value = anonymized_values[i];
    ASSERT_TRUE(anonymized_value.IsDocument());
    GeoPoint anonymized_point{anonymized_value["lat"].As<double>(),
                              anonymized_value["lon"].As<double>()};

    const auto& expected_value = expected_values[i];
    ASSERT_TRUE(expected_value.IsDocument());
    GeoPoint expected_point{expected_value["lat"].As<double>(),
                            expected_value["lon"].As<double>()};

    ASSERT_EQ(anonymized_point.lat, expected_point.lat);
    ASSERT_EQ(anonymized_point.lon, expected_point.lon);
  }

  ASSERT_EQ(anonymized_values, expected_values);
}
