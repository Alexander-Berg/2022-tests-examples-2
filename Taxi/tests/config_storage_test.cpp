#include <geo-pipeline/config/config_storage.hpp>
#include "config_diff_listener.hpp"
#include "pipeline_generator.hpp"

#include <userver/utest/utest.hpp>

#include <iostream>

namespace {
using GeoPipelineConfigDiff = ::geo_pipeline::config::GeoPipelineConfigDiff<
    geo_pipeline_config::PipelineTypesOfVersion<3>>;
using PipelineConfigHolder = ::geo_pipeline::config::PipelineConfigHolder<
    geo_pipeline_config::PipelineTypesOfVersion<3>>;
using PipelineConfig =
    geo_pipeline_config::PipelineTypesOfVersion<3>::PipelineConfig;
using PipelineConfigMap =
    geo_pipeline_config::PipelineTypesOfVersion<3>::PipelineConfigMap;

UTEST(ConfigStorageTest, DefaultConfig) {
  PipelineConfigHolder config_holder;
  auto config_ptr = config_holder.GetPipelineConfig();
  ASSERT_EQ(*config_ptr, PipelineConfigMap{});
}

UTEST(ConfigStorageTest, LoadConfigOnce) {
  PipelineGenerator gen;
  auto pipeline1 = gen.GeneratePipeline();

  PipelineConfigMap config1 = {{"pipeline1", pipeline1}};

  PipelineConfigHolder config_holder;
  config_holder.OnConfigUpdate(config1);
  auto config_ptr = config_holder.GetPipelineConfig();
  ASSERT_EQ(*config_ptr, config1);
}

UTEST(ConfigStorageTest, SimpleListener) {
  PipelineGenerator gen;
  auto pipeline1 = gen.GeneratePipeline();

  PipelineConfigMap config1 = {{"pipeline1", pipeline1}};

  PipelineConfigHolder config_holder;
  DiffListener diff_listener;
  config_holder.AddSubscription(
      [&diff_listener](const auto& diff) { diff_listener.Callback(diff); });
  ASSERT_EQ(diff_listener.GetDiff(), GeoPipelineConfigDiff{});
  config_holder.OnConfigUpdate(config1);
  auto config_ptr = config_holder.GetPipelineConfig();
  ASSERT_EQ(*config_ptr, config1);
  GeoPipelineConfigDiff expectd_diff{config1, {}};
  ASSERT_EQ(diff_listener.GetDiff(), expectd_diff);
}

UTEST(ConfigStorageTest, AddNewPipeline) {
  PipelineGenerator gen;
  auto pipeline1 = gen.GeneratePipeline();
  auto pipeline2 = gen.GeneratePipeline();

  PipelineConfigMap config1 = {{"pipeline1", pipeline1}};
  PipelineConfigMap config2 = {{"pipeline1", pipeline1},
                               {"pipeline2", pipeline2}};

  PipelineConfigHolder config_holder;
  DiffListener diff_listener;
  config_holder.AddSubscription(
      [&diff_listener](const auto& diff) { diff_listener.Callback(diff); });
  config_holder.OnConfigUpdate(config1);

  config_holder.OnConfigUpdate(config2);

  GeoPipelineConfigDiff expectd_diff{{{"pipeline2", pipeline2}}, {}};
  ASSERT_EQ(diff_listener.GetDiff(), expectd_diff);
}

UTEST(ConfigStorageTest, DeletePipeline) {
  PipelineGenerator gen;
  auto pipeline1 = gen.GeneratePipeline();
  auto pipeline2 = gen.GeneratePipeline();

  PipelineConfigMap config1 = {{"pipeline1", pipeline1},
                               {"pipeline2", pipeline2}};
  PipelineConfigMap config2 = {{"pipeline1", pipeline1}};

  PipelineConfigHolder config_holder;
  DiffListener diff_listener;
  config_holder.AddSubscription(
      [&diff_listener](const auto& diff) { diff_listener.Callback(diff); });
  config_holder.OnConfigUpdate(config1);

  config_holder.OnConfigUpdate(config2);

  GeoPipelineConfigDiff expectd_diff{{}, {{"pipeline2", pipeline2}}};
  ASSERT_EQ(diff_listener.GetDiff(), expectd_diff);
}

UTEST(ConfigStorageTest, RenamePipeline) {
  PipelineGenerator gen;
  auto pipeline1 = gen.GeneratePipeline();

  PipelineConfigMap config1 = {{"pipeline1", pipeline1}};
  PipelineConfigMap config2 = {{"pipeline2", pipeline1}};

  PipelineConfigHolder config_holder;
  DiffListener diff_listener;
  config_holder.AddSubscription(
      [&diff_listener](const auto& diff) { diff_listener.Callback(diff); });
  config_holder.OnConfigUpdate(config1);

  config_holder.OnConfigUpdate(config2);

  GeoPipelineConfigDiff expectd_diff{{{"pipeline2", pipeline1}},
                                     {{"pipeline1", pipeline1}}};
  ASSERT_EQ(diff_listener.GetDiff(), expectd_diff);
}

UTEST(ConfigStorageTest, ChangePipeline) {
  PipelineGenerator gen;
  auto pipeline1 = gen.GeneratePipeline();
  auto pipeline1_new = gen.GeneratePipeline(true);
  auto pipeline2 = gen.GeneratePipeline();

  PipelineConfigMap config1 = {{"pipeline1", pipeline1},
                               {"pipeline2", pipeline2}};
  PipelineConfigMap config2 = {{"pipeline1", pipeline1_new},
                               {"pipeline2", pipeline2}};

  PipelineConfigHolder config_holder;
  DiffListener diff_listener;
  config_holder.AddSubscription(
      [&diff_listener](const auto& diff) { diff_listener.Callback(diff); });
  config_holder.OnConfigUpdate(config1);

  config_holder.OnConfigUpdate(config2);

  GeoPipelineConfigDiff expectd_diff{{{"pipeline1", pipeline1_new}}, {}};
  ASSERT_EQ(diff_listener.GetDiff(), expectd_diff);
}
}  // namespace
