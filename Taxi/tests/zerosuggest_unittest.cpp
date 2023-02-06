#include <gtest/gtest.h>
#include <fstream>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>

#include "models/geosuggest/zerosuggest/candidates_extractor.hpp"
#include "models/geosuggest/zerosuggest/features_extractor.hpp"
#include "models/geosuggest/zerosuggest/objects.hpp"
#include "views/geosuggest/serializers.hpp"

using namespace models::geosuggest;
using namespace models::geosuggest::zerosuggest;
using namespace views::geosuggest::serializers;
using namespace utils::helpers;

Request RequestFromJson(const Json::Value& doc) {
  Request request;
  FetchMember(request.time, doc, "time");
  const auto& inner_doc = FetchObject(doc, "request");
  FetchMember(request.point_type, inner_doc, "type");
  FetchMember(request.lang, inner_doc, "lang");
  FetchAppInfo(request.app_info, inner_doc, "application_info");
  FetchAppState(request.app_state, inner_doc, "state");
  for (const auto& order_doc : FetchArray(doc, "orders")) {
    request.orders.emplace_back(OrderFromJson(order_doc));
  }
  for (const auto& offer_doc : FetchArray(doc, "offers")) {
    request.offers.emplace_back(OfferFromJson(offer_doc));
  }
  for (const auto& userplace_doc : FetchArray(doc, "userplaces")) {
    request.userplaces.emplace_back(UserplaceFromJson(userplace_doc));
  }
  return request;
}

Features FeaturesFromJson(const Json::Value& doc) {
  Features features;
  for (const auto& row_doc : FetchArray(doc, "numerical")) {
    std::vector<float> row;
    for (const auto& item : row_doc) {
      row.push_back(item.asFloat());
    }
    features.numerical.emplace_back(std::move(row));
  }
  for (const auto& row_doc : FetchArray(doc, "categorical")) {
    std::vector<std::string> row;
    for (const auto& item : row_doc) {
      row.emplace_back(item.asString());
    }
    features.categorical.emplace_back(std::move(row));
  }
  return features;
}

TEST(Zerosuggest, ExtractFeatures) {
  std::ifstream request_in(std::string(SOURCE_DIR) +
                           "/tests/static/zerosuggest_request.json");
  const auto request = RequestFromJson(ParseJson(request_in));

  std::ifstream features_in(std::string(SOURCE_DIR) +
                            "/tests/static/zerosuggest_features.json");
  const auto expected_features = FeaturesFromJson(ParseJson(features_in));

  const auto candidates_extractor = CandidatesExtractor(
      {{"userplace", "phone_history.source", "phone_history.destination",
        "phone_history.completion_point", "order_offers.source",
        "order_offers.destination"}});
  const auto candidates = candidates_extractor.Apply(
      request.userplaces, request.orders, request.offers);
  const auto features_extractor = FeaturesExtractor();
  const auto features = features_extractor.Apply(candidates, request);

  ASSERT_EQ(candidates.size(), expected_features.numerical.size());
  ASSERT_EQ(candidates.size(), expected_features.categorical.size());
  ASSERT_EQ(candidates.size(), features.numerical.size());
  ASSERT_EQ(candidates.size(), features.categorical.size());

  for (size_t index = 0; index < candidates.size(); ++index) {
    const auto& num_row = features.numerical[index];
    const auto& exp_num_row = expected_features.numerical[index];
    const auto& cat_row = features.categorical[index];
    const auto& exp_cat_row = expected_features.categorical[index];

    ASSERT_EQ(num_row.size(), exp_num_row.size());
    ASSERT_EQ(cat_row.size(), exp_cat_row.size());
    for (size_t jndex = 0; jndex < num_row.size(); ++jndex) {
      ASSERT_FLOAT_EQ(num_row[jndex], exp_num_row[jndex]);
    }
    for (size_t jndex = 0; jndex < cat_row.size(); ++jndex) {
      ASSERT_EQ(cat_row[jndex], exp_cat_row[jndex]);
    }
  }
}
