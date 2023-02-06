#include <gtest/gtest.h>
#include <fstream>

#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>
#include "models/pool/pool_model.hpp"

namespace {

ml::pool::ModelConfig GetTestConfig() {
  ml::pool::ModelConfig config;
  config.important_points = {{37.620379999999997, 55.753968999999998},
                             {37.538736, 55.749046},
                             {37.445399999999999, 55.881594999999997},
                             {37.565734999999997, 55.784838999999998},
                             {37.621319999999997, 55.705871999999999},
                             {37.634667, 55.791848999999999},
                             {37.632311000000001, 55.772641},
                             {37.583337999999998, 55.709330999999999},
                             {37.699252999999999, 55.748151999999997},
                             {37.726031999999996, 55.882407000000001},
                             {37.561022000000001, 55.720354},
                             {37.459569999999999, 55.638807},
                             {37.368580999999999, 55.748693000000003},
                             {37.788221999999998, 55.850143000000003},
                             {37.602483999999997, 55.882961999999999},
                             {37.896354000000002, 55.682071000000001},
                             {37.545492000000003, 55.431494999999998},
                             {37.409506999999998, 55.971567999999998},
                             {37.282375000000002, 55.603068999999998},
                             {37.900478999999997, 55.414347999999997},
                             {38.118087000000003, 55.561976000000001},
                             {37.567348000000003, 55.743299},
                             {37.656469000000001, 55.775500999999998},
                             {37.657764, 55.757185999999997},
                             {37.587845000000002, 55.73413}};
  config.random_coeffs_lon = {0.38173264265060425,  -0.44563794136047363,
                              -0.43460649251937866, -0.039558190852403641,
                              -0.06492556631565094, 0.19329224526882172,
                              -0.04344610869884491, -0.016625650227069855,
                              0.19322040677070618,  0.43008506298065186};
  config.random_coeffs_lat = {-0.36898490786552429, 0.36158990859985352,
                              0.14259512722492218,  -0.47535052895545959,
                              0.36592140793800354,  -0.34281787276268005,
                              0.48170489072799683,  -0.064561031758785248,
                              0.32892635464668274,  -0.2218547910451889};
  return config;
}

Json::Value GetTestJsonValue(const std::string& filename) {
  std::ifstream request_file(std::string(SOURCE_DIR) + "/tests/static/" +
                             filename + ".json");
  return utils::helpers::ParseJson(request_file);
}

class TestPoolModel : public ml::pool::PoolModel {
 public:
  using ml::pool::PoolModel::PoolModel;

  ml::pool::FeatureArray GetTestFeatures(const Json::Value& data) const {
    TimeStorage ts("pool_unittest");
    return ml::pool::PoolModel::GetFeatures(RequestData(data), ts);
  }
};

void CheckFeatures(const std::string& filename) {
  auto config = std::make_shared<ml::pool::ModelConfig>(GetTestConfig());
  auto data = GetTestJsonValue(filename);
  auto features = TestPoolModel(config).GetTestFeatures(data);
  ml::pool::FeatureArray true_features;
  for (const auto& feature :
       utils::helpers::FetchArray(data, "true_features")) {
    true_features.emplace_back(feature.asDouble());
  }
  ASSERT_TRUE(features.size() == true_features.size());
  for (unsigned i = 0; i < true_features.size(); ++i) {
    ASSERT_FLOAT_EQ(features[i], true_features[i])
        << "Wrong feature #" << std::to_string(i);
  }
}

TEST(Pool, GetFeatures) { CheckFeatures("pool_request"); }

}  // namespace
