#include "value_expanded.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include "config.hpp"

namespace {

struct UnpackKeyParam {
  std::string key;
  std::vector<std::string> result;
  std::string experiment;
};

class UnpackKeyParams : public testing::Test,
                        public testing::WithParamInterface<UnpackKeyParam> {};

}  // namespace

TEST_P(UnpackKeyParams, One) {
  const auto& param = GetParam();

  std::set<std::string> experiments;
  const auto& res = config::detail::UnpackZoneKey(param.key, experiments);
  EXPECT_EQ(param.result, res);
  if (param.experiment.empty()) {
    EXPECT_TRUE(experiments.empty());
  } else {
    EXPECT_EQ(1u, experiments.size());
    EXPECT_EQ(1u, experiments.count(param.experiment));
  }
}

INSTANTIATE_TEST_CASE_P(
    Serial, UnpackKeyParams,
    testing::Values(
        UnpackKeyParam{"__default__", {"::"}, ""},
        UnpackKeyParam{"", {"::"}, ""}, UnpackKeyParam{"msk", {"::msk"}, ""},
        UnpackKeyParam{"msk,tula,uzl", {"::msk", "::tula", "::uzl"}, ""},
        UnpackKeyParam{":msk", {"::msk"}, ""},
        UnpackKeyParam{"::msk", {"::msk"}, ""},
        UnpackKeyParam{"exp_name:msk", {":exp_name:msk"}, "exp_name"},
        UnpackKeyParam{"exp_name:msk,omsk",
                       {":exp_name:msk", ":exp_name:omsk"},
                       "exp_name"},
        UnpackKeyParam{"tag_name::msk", {"tag_name::msk"}, ""},
        UnpackKeyParam{
            "tag_name::msk,omsk", {"tag_name::msk", "tag_name::omsk"}, ""},
        UnpackKeyParam{
            "tag_name:exp_name:msk", {"tag_name:exp_name:msk"}, "exp_name"},
        UnpackKeyParam{"tag_name:exp_name:msk,omsk",
                       {"tag_name:exp_name:msk", "tag_name:exp_name:omsk"},
                       "exp_name"}), );

namespace {

struct GenerateKeyParam {
  std::string tag;
  std::string experiment;
  std::string zone;
  std::string result;
};

class GenerateKeyParams : public testing::Test,
                          public testing::WithParamInterface<GenerateKeyParam> {
};

}  // namespace

TEST_P(GenerateKeyParams, One) {
  const auto& param = GetParam();
  EXPECT_EQ(param.result, config::detail::GenerateZoneKey(
                              param.tag, param.experiment, param.zone));
}

INSTANTIATE_TEST_CASE_P(Serial, GenerateKeyParams,
                        testing::Values(GenerateKeyParam{"", "", "", "::"},
                                        GenerateKeyParam{"", "", "a", "::a"},
                                        GenerateKeyParam{"", "b", "a", ":b:a"},
                                        GenerateKeyParam{"c", "b", "a",
                                                         "c:b:a"}), );

namespace {

struct ValueZoneMapParam {
  std::string tag;
  std::set<std::string> experiments;
  std::string zone;
  int result;
};

class ValueZoneMapParams
    : public testing::Test,
      public testing::WithParamInterface<ValueZoneMapParam> {
 public:
  static void SetUpTestCase() {
    const std::map<std::string, int> data = {
        {"__default__", 0},
        {"msk", 1},
        {"tula,omsk", 2},
        {"exp_a:tula,omsk", 3},
        {"tag_a::__default__", 4},
        {"tag_a::spb,riga", 5},
        {"tag_a:exp_b:spb,riga", 6},
    };

    config::DocsMap docs_map;
    docs_map.Override("CHECK", data);

    map_s = std::make_unique<config::ValueZoneMap<int>>("CHECK", docs_map);
  }

  static void TearDownTestCase() { map_s.reset(); }

 protected:
  static std::unique_ptr<config::ValueZoneMap<int>> map_s;
};

std::unique_ptr<config::ValueZoneMap<int>> ValueZoneMapParams::map_s;

}  // namespace

TEST_P(ValueZoneMapParams, Check) {
  const auto& param = GetParam();
  EXPECT_EQ(param.result, map_s->Get(param.tag, param.experiments, param.zone));
}

INSTANTIATE_TEST_CASE_P(
    Serial, ValueZoneMapParams,
    testing::Values(ValueZoneMapParam{"", {}, "", 0},
                    ValueZoneMapParam{"tag_z", {}, "", 0},
                    ValueZoneMapParam{"", {}, "tomsk", 0},
                    ValueZoneMapParam{"", {"exp_a", "exp_b"}, "msk", 1},
                    ValueZoneMapParam{"tag_z", {}, "msk", 1},
                    ValueZoneMapParam{"", {"exp_z"}, "tula", 2},
                    ValueZoneMapParam{"", {"exp_z"}, "omsk", 2},
                    ValueZoneMapParam{"", {"exp_a"}, "tula", 3},
                    ValueZoneMapParam{"", {"exp_a"}, "omsk", 3},
                    ValueZoneMapParam{"tag_a", {}, "", 4},
                    ValueZoneMapParam{"tag_a", {}, "omsk", 4},
                    ValueZoneMapParam{"tag_a", {"exp_a"}, "tula", 4},
                    ValueZoneMapParam{"tag_a", {}, "riga", 5},
                    ValueZoneMapParam{"tag_a", {}, "spb", 5},
                    ValueZoneMapParam{"tag_a", {"exp_a"}, "riga", 5},
                    ValueZoneMapParam{"tag_a", {"exp_a"}, "spb", 5},
                    ValueZoneMapParam{"tag_a", {"exp_b"}, "riga", 6},
                    ValueZoneMapParam{"tag_a", {"exp_b"}, "spb", 6}), );

namespace {

class ValueZoneMapRegressParams
    : public testing::Test,
      public testing::WithParamInterface<ValueZoneMapParam> {
 public:
  static void SetUpTestCase() {
    const std::map<std::string, int> data = {
        {"__default__", 0},    {"calculator:yamaps_experiment_25:", 1},
        {"router_yamaps:", 2}, {"sochi", 3},
        {"tumen", 4},
    };

    config::DocsMap docs_map;
    docs_map.Override("CHECK", data);

    map_s = std::make_unique<config::ValueZoneMap<int>>("CHECK", docs_map);
  }

  static void TearDownTestCase() { map_s.reset(); }

 protected:
  static std::unique_ptr<config::ValueZoneMap<int>> map_s;
};

std::unique_ptr<config::ValueZoneMap<int>> ValueZoneMapRegressParams::map_s;

}  // namespace

TEST_P(ValueZoneMapRegressParams, Check) {
  const auto& param = GetParam();
  EXPECT_EQ(param.result, map_s->Get(param.tag, param.experiments, param.zone));
}

INSTANTIATE_TEST_CASE_P(
    Serial, ValueZoneMapRegressParams,
    testing::Values(
        ValueZoneMapParam{"", {}, "", 0},
        ValueZoneMapParam{"calculator", {"yamaps_experiment_25"}, "", 1},
        ValueZoneMapParam{"", {"router_yamaps"}, "", 2},
        ValueZoneMapParam{"", {}, "sochi", 3},
        ValueZoneMapParam{"", {}, "tumen", 4},
        // regress
        ValueZoneMapParam{"", {"yamaps_experiment_25"}, "", 0},
        ValueZoneMapParam{"", {"yamaps_experiment_25"}, "sochi", 3},
        ValueZoneMapParam{"", {"yamaps_experiment_25"}, "tumen", 4},
        ValueZoneMapParam{
            "", {"yamaps_experiment_25", "router_yamaps"}, "", 2}), );
