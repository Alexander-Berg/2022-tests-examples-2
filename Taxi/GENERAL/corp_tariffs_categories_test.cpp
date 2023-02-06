#include <gtest/gtest.h>

#include <testing/source_path.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include <helpers/corp_tariffs.hpp>

namespace {

const std::string kCorpTariffResponseFileName{
    utils::CurrentSourcePath("src/helpers/test_data/corp_tariffs.json")};

std::vector<std::string> GetExpectedCategories(
    const formats::json::Value& response_json) {
  EXPECT_TRUE(response_json.HasMember("categories") &&
              response_json["categories"].IsArray());

  std::vector<std::string> result;
  result.reserve(response_json["categories"].GetSize());
  for (const auto& item : response_json["categories"]) {
    EXPECT_TRUE(item.IsObject() && item.HasMember("id") &&
                item["id"].IsString());

    result.push_back(item["id"].As<std::string>());
  }
  return result;
}

void Compare(const models::CategoriesByIdMap& actual_categories,
             const std::vector<std::string>& expected_categories) {
  const auto assert_helper =
      [&actual_categories](
          [[maybe_unused]] const char* expr,
          const std::string& checked) -> testing::AssertionResult {
    if (actual_categories.count(checked)) {
      return testing::AssertionSuccess();
    }
    return testing::AssertionFailure()
           << "Expected: `" << checked
           << "` in parsed corp tariff categories\n  Actual: false";
  };

  for (const auto& each : expected_categories) {
    EXPECT_PRED_FORMAT1(assert_helper, each);
  }
  EXPECT_EQ(expected_categories.size(), actual_categories.size());
}

}  // namespace

TEST(CorpTariff, ParseCategories) {
  const auto& response_json =
      formats::json::blocking::FromFile(kCorpTariffResponseFileName);
  EXPECT_TRUE(response_json.HasMember("tariff") &&
              response_json["tariff"].IsObject());
  EXPECT_FALSE(response_json.HasMember("disable_surge"));
  const auto& expected_categories =
      GetExpectedCategories(response_json["tariff"]);

  const auto& response = clients::corp_tariffs::Parse(
      response_json, formats::parse::To<helpers::corp_tariffs::TariffCorp>{});

  for (const auto& one_category : response.tariff.categories) {
    if (one_category.id == "c4ecb891ee0241518869042718407f37") {
      EXPECT_EQ(one_category.disable_surge, false);
    } else {
      EXPECT_EQ(one_category.disable_surge, true);
    }
  }

  const auto& actual_categories =
      helpers::corp_tariffs::GetTariffCategories(response.tariff);

  for (const auto& [category_name, ptr_to_category] : actual_categories) {
    if (ptr_to_category->id == "c4ecb891ee0241518869042718407f37") {
      EXPECT_EQ(ptr_to_category->disable_surge, false);
    } else {
      EXPECT_EQ(ptr_to_category->disable_surge, true);
    }
  }

  Compare(actual_categories, expected_categories);
}
