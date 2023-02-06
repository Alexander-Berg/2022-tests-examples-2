#include <gtest/gtest.h>

#include <search/market/foodtech_cgi/join.hpp>
#include <search/market/foodtech_cgi/parts/join.hpp>
#include <search/market/foodtech_cgi/parts/parts.hpp>

namespace grocery_api {

namespace foodtech_cgi = grocery_api::search::market::foodtech_cgi;

TEST(TestJoinFoodtechCgi, Smoke) {
  foodtech_cgi::FoodtechCgiParts parts;
  parts.push_back(foodtech_cgi::UsePopularity{
      grocery_api::models::UsePopularityFlow::kUseNormalizedPopularity});
  parts.push_back(foodtech_cgi::UsePrivateLabel{true});
  parts.push_back(foodtech_cgi::UseFrontMargin{true});

  foodtech_cgi::FoodtechCgi foodtech_cgi;

  const auto joined = foodtech_cgi::Join(parts, std::move(foodtech_cgi));
  const foodtech_cgi::FoodtechCgi expected{
      "use-popularity-normalized=1&use-private-label=1&use-front-margin=1"};

  ASSERT_EQ(joined, expected);
}

}  // namespace grocery_api
