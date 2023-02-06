#include <gtest/gtest.h>
#include <fstream>

#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>

#include "common/datetime.hpp"
#include "models/user_order_fakeness/constants.hpp"
#include "models/user_order_fakeness/structs.hpp"
#include "models/user_order_fakeness/v1/model.hpp"

namespace {

const std::string kTestDataDir = std::string(SOURCE_DIR) + "/tests/static/";

class UserOrderFakenessModelMock
    : public ml::user_order_fakeness::v1::UserOrderFakenessModel {
 public:
  UserOrderFakenessModelMock(){};

  std::vector<float> ExtractNumFeaturesMock(
      const cctz::civil_second& datetime,
      const ml::user_order_fakeness::OrderRequest& order_request,
      const ml::user_order_fakeness::UserAggregates& user_aggregates) const {
    return ExtractNumFeatures(datetime, order_request, user_aggregates);
  }
  std::vector<std::string> ExtractCatFeaturesMock(
      const cctz::civil_second& datetime,
      const ml::user_order_fakeness::OrderRequest& order_request,
      const ml::user_order_fakeness::UserAggregates& user_aggregates) const {
    return ExtractCatFeatures(datetime, order_request, user_aggregates);
  }
};

Json::Value ReadJsonRequest(const std::string& filename) {
  std::ifstream request_file(std::string(SOURCE_DIR) + "/tests/static/" +
                             filename + ".json");
  return utils::helpers::ParseJson(request_file);
}

std::vector<float> ReadNumFeatures(const std::string& filename) {
  std::ifstream in(kTestDataDir + filename);
  Json::Value doc = utils::helpers::ParseJson(in);

  std::vector<float> features;
  for (auto it = doc.begin(); it != doc.end(); ++it) {
    features.push_back((*it).asFloat());
  }
  return features;
}

std::vector<std::string> ReadCatFeatures(const std::string& filename) {
  std::ifstream in(kTestDataDir + filename);
  Json::Value doc = utils::helpers::ParseJson(in);

  std::vector<std::string> features;
  for (auto it = doc.begin(); it != doc.end(); ++it) {
    features.push_back((*it).asString());
  }
  return features;
}

TEST(UserOrderFakeness, ExtractNumFeatures) {
  UserOrderFakenessModelMock model;

  const auto request = ReadJsonRequest("user_order_fakeness_request");

  std::string time_str;
  utils::helpers::FetchMember(time_str, request, "datetime");
  const auto datetime = ml::common::ParseDatetime(
      time_str, ml::user_order_fakeness::kFormatDateTime);
  const auto& order_request =
      ml::user_order_fakeness::OrderRequest::FromJson(request);
  const auto& user_aggregates =
      ml::user_order_fakeness::UserAggregates::FromJson(request);

  const auto gold_num_features =
      ReadNumFeatures("user_order_fakeness_num_features.json");
  const auto gold_cat_features =
      ReadCatFeatures("user_order_fakeness_cat_features.json");

  auto num_features =
      model.ExtractNumFeaturesMock(datetime, order_request, user_aggregates);
  for (unsigned int i = 0; i < num_features.size(); ++i) {
    ASSERT_FLOAT_EQ(num_features[i], gold_num_features[i]);
  }

  auto cat_features =
      model.ExtractCatFeaturesMock(datetime, order_request, user_aggregates);
  for (unsigned int i = 0; i < cat_features.size(); ++i) {
    ASSERT_EQ(cat_features[i], gold_cat_features[i]);
  }
}

}  // namespace
