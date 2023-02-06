#include <gtest/gtest.h>
#include <common/catboost_wrapper.hpp>
#include <fstream>
#include <string>

TEST(Catboost, WithCategoricalFeatures) {
  std::ifstream input_stream(std::string(SOURCE_DIR) +
                             "/tests/static/catboost/catboost_with_cats.cbm");
  std::vector<char> file_contents(
      (std::istreambuf_iterator<char>(input_stream)),
      std::istreambuf_iterator<char>());

  utils::catboost::CatboostWrapper info(file_contents);

  std::vector<float> float_features{1.66305173, -0.56335046, -0.14053091,
                                    0.71987214, 0.73619894,  -0.65750709,
                                    0.46593486, -0.92545095};
  std::vector<std::string> cat_features{"x0.0", "x-2.0"};

  ASSERT_FLOAT_EQ(info.Calc(float_features, cat_features), 100.153235);

  std::vector<std::vector<float>> float_features_vec{
      float_features, float_features, float_features};
  std::vector<std::vector<std::string>> cat_features_vec{
      cat_features, cat_features, cat_features};

  for (const auto prediction :
       info.Calc(float_features_vec, cat_features_vec)) {
    ASSERT_FLOAT_EQ(prediction, 100.153235);
  }
}

TEST(Catboost, WithoutCategoricalFeatures) {
  std::ifstream input_stream(
      std::string(SOURCE_DIR) +
      "/tests/static/catboost/catboost_without_cats.cbm");
  std::vector<char> file_contents(
      (std::istreambuf_iterator<char>(input_stream)),
      std::istreambuf_iterator<char>());

  utils::catboost::CatboostWrapper info(file_contents);

  std::vector<float> float_features{1.66305173, -0.56335046, -0.14053091,
                                    0.71987214, 0.73619894,  -0.65750709,
                                    0.46593486, -0.92545095};

  ASSERT_FLOAT_EQ(info.Calc(float_features), 138.99101);

  std::vector<std::vector<float>> float_features_vec{
      float_features, float_features, float_features};

  for (const auto prediction : info.Calc(float_features_vec)) {
    ASSERT_FLOAT_EQ(prediction, 138.99101);
  }
}
