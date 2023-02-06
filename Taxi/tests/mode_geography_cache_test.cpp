#include <set>
#include <variant>

#include <gtest/gtest.h>

#include <fmt/format.h>

#include <testing/taxi_config.hpp>

#include <taxi_config/variables/DRIVER_MODE_GEOGRAPHY_DEFAULTS.hpp>
#include <taxi_config/variables/DRIVER_MODE_GROUPS.hpp>

#include <caches/mode_geography_cache.hpp>
#include <models/geo_hierarchy.hpp>
#include <models/mode_rules/mode_rule.hpp>

using namespace utils::datetime;

namespace {

const models::GeoNode kGeoNode1{"geo_node1"};
const models::GeoNode kGeoNode2{"geo_node2"};
const models::GeoNode kGeoNode3{"geo_node3"};
const models::GeoNode kGeoNode4{"geo_node4"};

const driver_mode::WorkMode kWorkMode1{"mode1"};
const driver_mode::WorkMode kWorkMode2{"mode2"};
const driver_mode::WorkMode kWorkMode3{"mode3"};
const driver_mode::WorkMode kOrdersWorkMode{"orders"};

const models::mode_geography::ExperimentName kExperiment1{"exp1"};
const models::mode_geography::ExperimentName kExperiment2{"exp2"};

models::mode_rules::ModeRule CreateModeRule(
    const driver_mode::WorkMode& work_mode) {
  // We use only work mode and offers group so other fields left unspecified
  models::mode_rules::ModeRule mode_rule{};
  mode_rule.work_mode = work_mode;
  mode_rule.offers_group = models::OffersGroup{"taxi"};
  return mode_rule;
}

const models::mode_rules::ModeRule kMode1 = CreateModeRule(kWorkMode1);
const models::mode_rules::ModeRule kMode2 = CreateModeRule(kWorkMode2);
const models::mode_rules::ModeRule kMode3 = CreateModeRule(kWorkMode3);
const models::mode_rules::ModeRule kOrdersMode =
    CreateModeRule(kOrdersWorkMode);

caches::mode_geography::Cache CreateCache() {
  caches::mode_geography::Cache result;

  result.InsertOrAssignFromModel(models::GeoNode{kGeoNode1},
                                 driver_mode::WorkMode{kWorkMode1},
                                 {true, {{kExperiment1, {true}}}});

  result.InsertOrAssignFromModel(models::GeoNode{kGeoNode2},
                                 driver_mode::WorkMode{kWorkMode1},
                                 {false, {{kExperiment1, {false}}}});

  result.InsertOrAssignFromModel(models::GeoNode{kGeoNode3},
                                 driver_mode::WorkMode{kWorkMode1},
                                 {true, {{kExperiment2, {true}}}});

  result.InsertOrAssignFromModel(models::GeoNode{kGeoNode4},
                                 driver_mode::WorkMode{kWorkMode1},
                                 {false, {}});

  result.InsertOrAssignFromModel(models::GeoNode{kGeoNode1},
                                 driver_mode::WorkMode{kWorkMode2},
                                 {false, {}});

  result.InsertOrAssignFromModel(models::GeoNode{kGeoNode2},
                                 driver_mode::WorkMode{kWorkMode2}, {true, {}});

  result.InsertOrAssignFromModel(models::GeoNode{kGeoNode1},
                                 driver_mode::WorkMode{kOrdersWorkMode},
                                 {false, {}});

  return result;
}

void CheckExperimentsEqual(
    const models::mode_geography::Experiments& actual_experiments,
    const std::set<models::mode_geography::ExperimentName>&
        expected_enabled_experiment_names,
    const std::string& label) {
  EXPECT_EQ(
      std::count_if(actual_experiments.begin(), actual_experiments.end(),
                    [](const auto& e) { return e.second.is_enabled == true; }),
      expected_enabled_experiment_names.size())
      << label;

  for (const auto& [experiment_name, experiment_settings] :
       actual_experiments) {
    if (experiment_settings.is_enabled) {
      EXPECT_EQ(expected_enabled_experiment_names.count(experiment_name), 1)
          << fmt::format("{}: experiment {} expected to be enabled", label,
                         experiment_name);
    } else {
      EXPECT_EQ(expected_enabled_experiment_names.count(experiment_name), 0)
          << fmt::format("{}: experiment {} expected to be disabled", label,
                         experiment_name);
    }
  }
}

}  // namespace

TEST(CheckModeAvailability, IncludeModeTest) {
  const auto& default_config = dynamic_config::GetDefaultSnapshot();

  const dynamic_config::StorageMock storage_mock(
      {{taxi_config::DRIVER_MODE_GROUPS,
        default_config[taxi_config::DRIVER_MODE_GROUPS]},
       {taxi_config::DRIVER_MODE_GEOGRAPHY_DEFAULTS,
        default_config[taxi_config::DRIVER_MODE_GEOGRAPHY_DEFAULTS]}});

  const auto config = storage_mock.GetSnapshot();

  const auto cache = CreateCache();

  {
    EXPECT_TRUE(cache.ModeHasGeography(kMode1, config));
    EXPECT_TRUE(cache.ModeHasGeography(kMode2, config));
    EXPECT_TRUE(cache.ModeHasGeography(kMode3, config));
  }

  {
    const auto geo_config = cache.GetConfiguration(kMode1, {{kGeoNode1}});
    EXPECT_TRUE(geo_config.is_enabled == true) << "Enabled in root";
  }

  {
    const auto geo_config = cache.GetConfiguration(kMode1, {{kGeoNode2}});
    EXPECT_TRUE(geo_config.is_enabled == false) << "Disabled in root";
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode1, {{kGeoNode2, kGeoNode1}});
    EXPECT_TRUE(geo_config.is_enabled == false) << "Disabled in child";
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode1, {{kGeoNode1, kGeoNode2}});
    EXPECT_TRUE(geo_config.is_enabled == true) << "Enabled in child";
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode1, {{kGeoNode1, kGeoNode2, kGeoNode3}});
    EXPECT_TRUE(geo_config.is_enabled == true) << "Re-enabled in child";
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode1, {{kGeoNode2, kGeoNode1, kGeoNode4}});
    EXPECT_TRUE(geo_config.is_enabled == false) << "Re-disabled in child";
  }

  // Enabled in parent node
  {
    const auto geo_config =
        cache.GetConfiguration(kMode2, {{kGeoNode4, kGeoNode3, kGeoNode1}});
    EXPECT_TRUE(geo_config.is_enabled == false) << "Enabled in parent node";
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode2, {{kGeoNode4, kGeoNode3, kGeoNode2}});
    EXPECT_TRUE(geo_config.is_enabled == true) << "Disabled in parent node";
  }

  {
    const auto geo_config = cache.GetConfiguration(kMode2, {{kGeoNode4}});
    EXPECT_TRUE(geo_config.is_enabled == false)
        << "Wrong hierarchy provided for hierarchical mode";
  }

  {
    const auto geo_config = cache.GetConfiguration(kMode3, {});
    EXPECT_TRUE(geo_config.is_enabled == false)
        << "No geonodes provided for not hierarchical mode";
  }

  {
    EXPECT_FALSE(cache.ModeHasGeography(kOrdersMode, config))
        << "Cannot disable reset mode from DRIVER_MODE_GROUPS";
  }
}

TEST(CheckModeAvailability, MergeModeExperimentsTest) {
  const auto cache = CreateCache();

  {
    const auto geo_config = cache.GetConfiguration(kMode1, {{kGeoNode1}});
    CheckExperimentsEqual(geo_config.experiments, {kExperiment1}, "From root");
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode1, {{kGeoNode1, kGeoNode3}});
    CheckExperimentsEqual(geo_config.experiments, {kExperiment1, kExperiment2},
                          "Merge two nodes");
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode1, {{kGeoNode2, kGeoNode1}});
    CheckExperimentsEqual(geo_config.experiments, {}, "Disabled in child");
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode1, {{kGeoNode1, kGeoNode2, kGeoNode1}});
    CheckExperimentsEqual(geo_config.experiments, {kExperiment1},
                          "Disabled in child than enabled");
  }

  {
    const auto geo_config =
        cache.GetConfiguration(kMode1, {{kGeoNode4, kGeoNode1, kGeoNode2}});
    CheckExperimentsEqual(geo_config.experiments, {kExperiment1},
                          "Enabled in child without exps");
  }
}
