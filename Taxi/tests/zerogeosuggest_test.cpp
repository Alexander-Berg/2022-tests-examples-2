#include <gtest/gtest.h>

#include <testing/source_path.hpp>
#include <userver/formats/json.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/fs/blocking/read.hpp>

#include <json-diff/json_diff.hpp>

#include <views/external/zerosuggest_geo.hpp>

namespace test::zerogeosuggest {

namespace {

formats::json::Value LoadJson(const std::string& file_name) {
  auto contents = fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/" + file_name));
  return formats::json::FromString(contents);
}

}  // namespace

TEST(TestZeroGeoSuggest, Loading) {
  auto contents = fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/zerogeosuggest.pb"));
  ::geosuggest::proto::ZeroSuggestResponseItems items_pb;
  (void)items_pb.ParseFromString(TProtoStringType(contents));
  std::vector<clients::yamaps_suggest_geo::AddressItem> result_pb;
  for (auto&& item : *items_pb.mutable_items()) {
    result_pb.push_back(umlaas_geo::views::ToJsonStructure(std::move(item)));
  }

  std::vector<clients::yamaps_suggest_geo::AddressItem> result;
  auto array = LoadJson("zerogeosuggest.json")["items"];
  array.CheckArrayOrNull();
  result.reserve(array.GetSize());
  for (const auto& item : array) {
    result.insert(result.end(),
                  item.As<clients::yamaps_suggest_geo::AddressItem>());
  }

  EXPECT_EQ(result_pb.size(), result.size());

  for (size_t i = 0; i < result_pb.size(); ++i) {
    auto& features = result[i].features.num.extra;
    auto& features_pb = result_pb[i].features.num.extra;
    for (auto& f : features) {
      auto it = features_pb.find(f.first);
      EXPECT_FALSE(it == features_pb.end());
      EXPECT_LT(std::abs(it->second - f.second), 0.000001);
      features_pb.erase(it);
    }
    features.clear();
    EXPECT_EQ(features_pb.size(), 0);
  }

  formats::json::ValueBuilder vb;
  vb["items"] = result;

  formats::json::ValueBuilder vb_pb;
  vb_pb["items"] = result_pb;

  EXPECT_PRED_FORMAT2(json_diff::AreValuesEqual, vb.ExtractValue(),
                      vb_pb.ExtractValue());
}

}  // namespace test::zerogeosuggest
