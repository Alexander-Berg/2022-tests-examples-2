#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/utils/boost_uuid4.hpp>

#include <discounts-match/matched_data.hpp>

namespace {

struct Data {
  int data = 0;
};

Data Parse(const formats::json::Value& elem, formats::parse::To<Data>) {
  return Data{elem["data"].As<int>()};
}

}  // namespace

TEST(MatchedData, MatcheDataCreatorsGet) {
  const auto creator =
      rules_match::MakeMatchedDataCreator<formats::json::Value>();
  const rules_match::MatchedDataCreators creators{
      {{"hierarchy_name", creator}}};

  EXPECT_NO_THROW(creators.Get("hierarchy_name"));
  EXPECT_TRUE(creators.Get("hierarchy_name"));
  EXPECT_THROW(creators.Get("missing_hierarchy_name"),
               rules_match::MatchedDataCreatorNotFoundError);
}

TEST(MatchedData, Parse) {
  EXPECT_NO_THROW((rules_match::MatchedData<Data>{
      rules_match::RulesMatchBase::DataId{1},
      utils::generators::GenerateBoostUuid(),
      formats::json::FromString("{\"data\":1}")}));

  EXPECT_THROW(
      (rules_match::MatchedData<Data>{rules_match::RulesMatchBase::DataId{2},
                                      utils::generators::GenerateBoostUuid(),
                                      formats::json::FromString("{}")}),
      rules_match::MatchedDataParseError);
}

TEST(MatchedData, Cast) {
  const auto matched_data =
      std::make_shared<const rules_match::MatchedData<Data>>(
          rules_match::RulesMatchBase::DataId{1},
          utils::generators::GenerateBoostUuid(),
          formats::json::FromString("{\"data\":1}"));

  const std::shared_ptr<const rules_match::BaseMatchedData> base_matched_data =
      matched_data;

  EXPECT_NO_THROW(rules_match::GetMatchedData<Data>(*matched_data));
  EXPECT_NO_THROW(rules_match::GetMatchedDataPtr<Data>(base_matched_data));

  EXPECT_THROW(rules_match::GetMatchedData<formats::json::Value>(*matched_data),
               rules_match::MatchedDataCastError);
  EXPECT_THROW(
      rules_match::GetMatchedDataPtr<formats::json::Value>(base_matched_data),
      rules_match::MatchedDataCastError);
}
