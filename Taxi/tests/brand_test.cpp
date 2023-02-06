#include "config/brand.hpp"
#include <gtest/gtest.h>
#include <unordered_map>
#include <unordered_set>
#include "utils/helpers/bson.hpp"
#include "utils/helpers/json.hpp"

namespace {

using TestMap =
    std::unordered_map<std::string, std::unordered_set<std::string>>;

TestMap ConvertToTestMap(const utils::brand::FriendBrandsMap& src) {
  TestMap result;
  for (auto [top_brand, ptr] : src) {
    auto& result_top_brand = result[top_brand];
    for (const auto& brand : *ptr) {
      result_top_brand.insert(brand);
    }
  }
  return result;
}

auto TryParseMap(const char* config) {
  config::DocsMap docs_map;
  docs_map.Override("FRIEND_BRANDS", utils::helpers::Json2Bson(
                                         utils::helpers::ParseJson(config)));
  return utils::brand::Config(docs_map).friend_brands_map;
}

}  // namespace

TEST(TestBrand, ParseConfigGood) {
  EXPECT_EQ(ConvertToTestMap(TryParseMap(R"(
      [
          [ "yauber", "yataxi" ],
          [ "yango" ]
      ]
  )")),
            (TestMap{{"yauber", {"yauber", "yataxi"}},
                     {"yataxi", {"yauber", "yataxi"}},
                     {"yango", {"yango"}}}));
}

TEST(TestBrand, ParseConfigBad) {
  EXPECT_THROW(TryParseMap(R"(
      [
          [ "yauber", "yataxi", "yango" ],
          [ "vezet", "yango" ]
      ]
  )"),
               std::logic_error);
}
