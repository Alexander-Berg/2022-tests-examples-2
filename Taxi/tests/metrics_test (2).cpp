#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>
#include <taxi_config/taxi_config.hpp>
#include <testing/taxi_config.hpp>
#include <userver/formats/json.hpp>

#include <components/buttons.hpp>
#include <models/context.hpp>
#include <models/entrypoints.hpp>
#include <utils/metrics.hpp>
#include "components/blocks.hpp"
#include "fixtures.hpp"

const std::string expected_shortcuts_metrics = R"({
    "undefined": {
        "media_stories": {
            "1": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "total": {
                "blender-shortcuts" : 2,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "position"
            }
        },
        "taxi_expected_destination": {
            "0": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "total": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "position"
            }
        },
        "eats_place": {
            "total": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "position"
            }
        },
        "$meta": {
            "solomon_children_labels": "scenario"
        }
    },
    "$meta": {
        "solomon_children_labels": "zone"
    }
})";

const std::string expected_shortcuts_scenario_distribution_metrics = R"({
    "undefined": {
        "taxi_expected_destination": {
            "1": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "distribution_bucket"
            }
        },
        "media_stories": {
            ">=2": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "distribution_bucket"
            }
        },
        "promo_stories": {
            "0": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "distribution_bucket"
            }
        },
        "eats_place": {
            "1": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels":"screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "distribution_bucket"
            }
        },
        "$meta": {
            "solomon_children_labels": "scenario"
        }
    },
    "$meta": {
        "solomon_children_labels": "zone"
    }
})";

const std::string expected_entrypoints_metrics = R"({
    "undefined": {
        "eats_based_grocery": {
            "bricks": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "entrypoint"
            }
        },
        "eats_based_eats": {
            "bricks": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "entrypoint"
            }
        },
        "discovery_drive": {
            "buttons": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "entrypoint"
            }
        },
        "discovery_masstransit": {
            "buttons": {
                "blender-shortcuts" : 1,
                "$meta" : {
                    "solomon_children_labels" : "screen"
                }
            },
            "$meta": {
                "solomon_children_labels": "entrypoint"
            }
        },
        "$meta": {
            "solomon_children_labels": "scenario"
        }
    },
    "$meta": {
        "solomon_children_labels": "zone"
    }
})";

TEST(TestMetrics, Format) {
  RunInCoro(
      [] {
        const auto& config = dynamic_config::GetDefaultSnapshot();
        auto taxi_config = config.Get<taxi_config::TaxiConfig>();
        taxi_config.shortcuts_scenario_size_to_metrics_settings.scenarios = {
            "taxi_expected_destination", "media_stories", "eats_place",
            "promo_stories"};

        utils::metrics::ShortcutsMetrics shortcuts_metrics;
        shortcuts_metrics.SendMetrics(std::nullopt,
                                      fixtures::BuildFakeBlocks(1), taxi_config,
                                      "blender-shortcuts");

        utils::metrics::ShortcutsScenarioDistributionMetrics
            shortcuts_scenario_distribution_metrics;
        shortcuts_scenario_distribution_metrics.SendMetrics(
            std::nullopt, fixtures::BuildFakeBlocks(1), taxi_config,
            "blender-shortcuts");

        utils::metrics::EntrypointsMetrics entrypoints_metrics;
        entrypoints_metrics.SendMetrics(std::nullopt,
                                        fixtures::BuildFakeInternalBricks(),
                                        fixtures::BuildFakeInternalButtons(),
                                        taxi_config, "blender-shortcuts");

        ASSERT_EQ(formats::json::FromString(expected_shortcuts_metrics),
                  shortcuts_metrics.ToJson());
        ASSERT_EQ(formats::json::FromString(
                      expected_shortcuts_scenario_distribution_metrics),
                  shortcuts_scenario_distribution_metrics.ToJson());
        ASSERT_EQ(formats::json::FromString(expected_entrypoints_metrics),
                  entrypoints_metrics.ToJson());
      },
      1);
}
