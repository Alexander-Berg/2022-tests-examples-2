#include <unordered_set>

#include <metrix/filter.hpp>
#include <metrix/writer.hpp>
#include <set-rules-matcher/matcher.hpp>
#include <taxi_config/taxi_config.hpp>
#include <taxi_config/variables/METRIX_AGGREGATION.hpp>
namespace metrix {
void Writer::PushMetric0(std::uint64_t value,
                         const std::optional<std::string>& agglomeration,
                         const std::optional<std::string>& service) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric0"}};
    if (agglomeration) {
      arguments.emplace("agglomeration:" + *agglomeration);
    }
    if (service) {
      arguments.emplace("service:" + *service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::Labels0 descr;
      descr.metric_name = "metric0";
      if (agglomeration) {
        auto label_opt =
            GetFilteredLabel("agglomeration", *agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (service) {
        auto label_opt = GetFilteredLabel("service", *service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    labels::Labels0 descr;
    descr.metric_name = "metric0";
    if (agglomeration) {
      descr.agglomeration = *agglomeration;
    }
    if (service) {
      descr.service = *service;
    }
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels0_counter_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) { counter.GetCurrentCounter() += value; }

    );
  }
}
void Writer::PushMetric1(std::chrono::microseconds value,
                         const std::optional<std::string>& agglomeration,
                         const std::optional<std::string>& dispatch_statuses,
                         const std::optional<std::string>& tariff_group,
                         const std::optional<std::string>& service) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric1"}};
    if (agglomeration) {
      arguments.emplace("agglomeration:" + *agglomeration);
    }
    if (dispatch_statuses) {
      arguments.emplace("dispatch_statuses:" + *dispatch_statuses);
    }
    if (tariff_group) {
      arguments.emplace("tariff_group:" + *tariff_group);
    }
    if (service) {
      arguments.emplace("service:" + *service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::Labels1> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::Labels1 descr;
      descr.metric_name = "metric1";
      if (agglomeration) {
        auto label_opt =
            GetFilteredLabel("agglomeration", *agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (dispatch_statuses) {
        auto label_opt =
            GetFilteredLabel("dispatch_statuses", *dispatch_statuses, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.dispatch_statuses = *label_opt;
      }
      if (tariff_group) {
        auto label_opt =
            GetFilteredLabel("tariff_group", *tariff_group, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.tariff_group = *label_opt;
      }
      if (service) {
        auto label_opt = GetFilteredLabel("service", *service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    labels::Labels1 descr;
    descr.metric_name = "metric1";
    if (agglomeration) {
      descr.agglomeration = *agglomeration;
    }
    if (dispatch_statuses) {
      descr.dispatch_statuses = *dispatch_statuses;
    }
    if (tariff_group) {
      descr.tariff_group = *tariff_group;
    }
    if (service) {
      descr.service = *service;
    }
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels1_time_counter_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter() += value.count();
        }

    );
  }
}
void Writer::PushMetric2(std::uint64_t value,
                         const std::optional<std::string>& agglomeration,
                         const std::optional<std::string>& service) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric2"}};
    if (agglomeration) {
      arguments.emplace("agglomeration:" + *agglomeration);
    }
    if (service) {
      arguments.emplace("service:" + *service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::Labels0 descr;
      descr.metric_name = "metric2";
      if (agglomeration) {
        auto label_opt =
            GetFilteredLabel("agglomeration", *agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (service) {
        auto label_opt = GetFilteredLabel("service", *service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    labels::Labels0 descr;
    descr.metric_name = "metric2";
    if (agglomeration) {
      descr.agglomeration = *agglomeration;
    }
    if (service) {
      descr.service = *service;
    }
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels0_percentile_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter().Account(value);
        }

    );
  }
}
void Writer::PushMetric2(const types::PercentileType& value,
                         const std::optional<std::string>& agglomeration,
                         const std::optional<std::string>& service) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric2"}};
    if (agglomeration) {
      arguments.emplace("agglomeration:" + *agglomeration);
    }
    if (service) {
      arguments.emplace("service:" + *service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::Labels0 descr;
      descr.metric_name = "metric2";
      if (agglomeration) {
        auto label_opt =
            GetFilteredLabel("agglomeration", *agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (service) {
        auto label_opt = GetFilteredLabel("service", *service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    labels::Labels0 descr;
    descr.metric_name = "metric2";
    if (agglomeration) {
      descr.agglomeration = *agglomeration;
    }
    if (service) {
      descr.service = *service;
    }
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels0_percentile_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter().Add(value);
        }

    );
  }
}
void Writer::PushMetric3(std::chrono::milliseconds value,
                         const std::optional<std::string>& agglomeration,
                         const std::optional<std::string>& dispatch_statuses,
                         const std::optional<std::string>& tariff_group,
                         const std::optional<std::string>& service) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric3"}};
    if (agglomeration) {
      arguments.emplace("agglomeration:" + *agglomeration);
    }
    if (dispatch_statuses) {
      arguments.emplace("dispatch_statuses:" + *dispatch_statuses);
    }
    if (tariff_group) {
      arguments.emplace("tariff_group:" + *tariff_group);
    }
    if (service) {
      arguments.emplace("service:" + *service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::Labels1> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::Labels1 descr;
      descr.metric_name = "metric3";
      if (agglomeration) {
        auto label_opt =
            GetFilteredLabel("agglomeration", *agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (dispatch_statuses) {
        auto label_opt =
            GetFilteredLabel("dispatch_statuses", *dispatch_statuses, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.dispatch_statuses = *label_opt;
      }
      if (tariff_group) {
        auto label_opt =
            GetFilteredLabel("tariff_group", *tariff_group, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.tariff_group = *label_opt;
      }
      if (service) {
        auto label_opt = GetFilteredLabel("service", *service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    labels::Labels1 descr;
    descr.metric_name = "metric3";
    if (agglomeration) {
      descr.agglomeration = *agglomeration;
    }
    if (dispatch_statuses) {
      descr.dispatch_statuses = *dispatch_statuses;
    }
    if (tariff_group) {
      descr.tariff_group = *tariff_group;
    }
    if (service) {
      descr.service = *service;
    }
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels1_time_percentile_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter().Account(value.count());
        }

    );
  }
}
void Writer::PushMetric3(const types::TimePercentileType& value,
                         const std::optional<std::string>& agglomeration,
                         const std::optional<std::string>& dispatch_statuses,
                         const std::optional<std::string>& tariff_group,
                         const std::optional<std::string>& service) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric3"}};
    if (agglomeration) {
      arguments.emplace("agglomeration:" + *agglomeration);
    }
    if (dispatch_statuses) {
      arguments.emplace("dispatch_statuses:" + *dispatch_statuses);
    }
    if (tariff_group) {
      arguments.emplace("tariff_group:" + *tariff_group);
    }
    if (service) {
      arguments.emplace("service:" + *service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::Labels1> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::Labels1 descr;
      descr.metric_name = "metric3";
      if (agglomeration) {
        auto label_opt =
            GetFilteredLabel("agglomeration", *agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (dispatch_statuses) {
        auto label_opt =
            GetFilteredLabel("dispatch_statuses", *dispatch_statuses, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.dispatch_statuses = *label_opt;
      }
      if (tariff_group) {
        auto label_opt =
            GetFilteredLabel("tariff_group", *tariff_group, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.tariff_group = *label_opt;
      }
      if (service) {
        auto label_opt = GetFilteredLabel("service", *service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    labels::Labels1 descr;
    descr.metric_name = "metric3";
    if (agglomeration) {
      descr.agglomeration = *agglomeration;
    }
    if (dispatch_statuses) {
      descr.dispatch_statuses = *dispatch_statuses;
    }
    if (tariff_group) {
      descr.tariff_group = *tariff_group;
    }
    if (service) {
      descr.service = *service;
    }
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels1_time_percentile_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter().Add(value);
        }

    );
  }
}
void Writer::PushMetric4(std::chrono::seconds value,
                         const std::optional<std::string>& agglomeration,
                         const std::optional<std::string>& service) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric4"}};
    if (agglomeration) {
      arguments.emplace("agglomeration:" + *agglomeration);
    }
    if (service) {
      arguments.emplace("service:" + *service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::Labels0 descr;
      descr.metric_name = "metric4";
      if (agglomeration) {
        auto label_opt =
            GetFilteredLabel("agglomeration", *agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (service) {
        auto label_opt = GetFilteredLabel("service", *service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    labels::Labels0 descr;
    descr.metric_name = "metric4";
    if (agglomeration) {
      descr.agglomeration = *agglomeration;
    }
    if (service) {
      descr.service = *service;
    }
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels0_avg_counter_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter().Account(value.count());
        }

    );
  }
}
::utils::ScopeGuard Writer::LapMetric5(
    const std::optional<std::string>& agglomeration,
    const std::optional<std::string>& service) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric5"}};
    if (agglomeration) {
      arguments.emplace("agglomeration:" + *agglomeration);
    }
    if (service) {
      arguments.emplace("service:" + *service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::Labels0 descr;
      descr.metric_name = "metric5";
      if (agglomeration) {
        auto label_opt =
            GetFilteredLabel("agglomeration", *agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (service) {
        auto label_opt = GetFilteredLabel("service", *service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    labels::Labels0 descr;
    descr.metric_name = "metric5";
    if (agglomeration) {
      descr.agglomeration = *agglomeration;
    }
    if (service) {
      descr.service = *service;
    }
    descrs.push_back(descr);
  }

  auto start = std::chrono::steady_clock::now();
  return ::utils::ScopeGuard{[this, start, descrs{std::move(descrs)}]() {
    auto stop = std::chrono::steady_clock::now();
    auto value =
        std::chrono::duration_cast<std::chrono::milliseconds>(stop - start)
            .count();
    for (auto& descr : descrs) {
      labels0_milli_lap_container_.InsertThenUpdate(
          descr,
          [&value](bool, auto& counter) {
            counter.GetCurrentCounter().Account(value);
          }

      );
    }
  }};
}
::utils::ScopeGuard Writer::LapMetric6() {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric6"}};
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::EmptyLabels> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::EmptyLabels descr;
      descr.metric_name = "metric6";
      descrs.push_back(descr);
    }
  } else {
    labels::EmptyLabels descr;
    descr.metric_name = "metric6";
    descrs.push_back(descr);
  }

  auto start = std::chrono::steady_clock::now();
  return ::utils::ScopeGuard{[this, start, descrs{std::move(descrs)}]() {
    auto stop = std::chrono::steady_clock::now();
    auto value =
        std::chrono::duration_cast<std::chrono::milliseconds>(stop - start)
            .count();
    for (auto& descr : descrs) {
      empty_labels_milli_lap_container_.InsertThenUpdate(
          descr,
          [&value](bool, auto& counter) {
            counter.GetCurrentCounter().Account(value);
          }

      );
    }
  }};
}
::utils::ScopeGuard Writer::PercentileLapMetric7() {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {{"metric_name:metric7"}};
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }

  std::vector<labels::EmptyLabels> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      labels::EmptyLabels descr;
      descr.metric_name = "metric7";
      descrs.push_back(descr);
    }
  } else {
    labels::EmptyLabels descr;
    descr.metric_name = "metric7";
    descrs.push_back(descr);
  }

  auto start = std::chrono::steady_clock::now();
  return ::utils::ScopeGuard{[this, start, descrs{std::move(descrs)}]() {
    auto stop = std::chrono::steady_clock::now();
    auto value =
        std::chrono::duration_cast<std::chrono::milliseconds>(stop - start)
            .count();
    for (auto& descr : descrs) {
      empty_labels_percentile_lap_container_.InsertThenUpdate(
          descr,
          [&value](bool, auto& counter) {
            counter.GetCurrentCounter().Account(value);
          }

      );
    }
  }};
}
void Writer::PushLabels0AvgCounter(std::chrono::seconds value,
                                   labels::Labels0 descr) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {
        {"metric_name:" + descr.metric_name}};
    if (descr.agglomeration.size()) {
      arguments.emplace("agglomeration:" + descr.agglomeration);
    }
    if (descr.service.size()) {
      arguments.emplace("service:" + descr.service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }
  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      if (descr.agglomeration.size()) {
        auto label_opt =
            GetFilteredLabel("agglomeration", descr.agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (descr.service.size()) {
        auto label_opt = GetFilteredLabel("service", descr.service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels0_avg_counter_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter().Account(value.count());
        }

    );
  }
}
void Writer::PushLabels0Counter(std::uint64_t value, labels::Labels0 descr) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {
        {"metric_name:" + descr.metric_name}};
    if (descr.agglomeration.size()) {
      arguments.emplace("agglomeration:" + descr.agglomeration);
    }
    if (descr.service.size()) {
      arguments.emplace("service:" + descr.service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }
  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      if (descr.agglomeration.size()) {
        auto label_opt =
            GetFilteredLabel("agglomeration", descr.agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (descr.service.size()) {
        auto label_opt = GetFilteredLabel("service", descr.service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels0_counter_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) { counter.GetCurrentCounter() += value; }

    );
  }
}
void Writer::PushLabels0Percentile(std::uint64_t value, labels::Labels0 descr) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {
        {"metric_name:" + descr.metric_name}};
    if (descr.agglomeration.size()) {
      arguments.emplace("agglomeration:" + descr.agglomeration);
    }
    if (descr.service.size()) {
      arguments.emplace("service:" + descr.service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }
  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      if (descr.agglomeration.size()) {
        auto label_opt =
            GetFilteredLabel("agglomeration", descr.agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (descr.service.size()) {
        auto label_opt = GetFilteredLabel("service", descr.service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels0_percentile_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter().Account(value);
        }

    );
  }
}
void Writer::PushLabels0Percentile(const types::PercentileType& value,
                                   labels::Labels0 descr) {
  std::vector<std::vector<taxi_config::metrix_aggregation::AggRule>>
      agg_rules{};
  const auto snapshot = taxi_cfg_.GetSnapshot();
  const auto& metrix_aggregation = snapshot[taxi_config::METRIX_AGGREGATION];
  if (!metrix_aggregation.empty()) {
    std::unordered_set<std::string> arguments = {
        {"metric_name:" + descr.metric_name}};
    if (descr.agglomeration.size()) {
      arguments.emplace("agglomeration:" + descr.agglomeration);
    }
    if (descr.service.size()) {
      arguments.emplace("service:" + descr.service);
    }
    auto it = set_rules_matcher::MatchRuleWithValue(
        metrix_aggregation.begin(), metrix_aggregation.end(), arguments);
    while (it != metrix_aggregation.end()) {
      agg_rules.emplace_back(it->value);
      it = set_rules_matcher::MatchRuleWithValue(
          it + 1, metrix_aggregation.end(), arguments);
    }
  }
  std::vector<labels::Labels0> descrs;
  if (!agg_rules.empty()) {
    for ([[maybe_unused]] auto& agg_rule : agg_rules) {
      if (descr.agglomeration.size()) {
        auto label_opt =
            GetFilteredLabel("agglomeration", descr.agglomeration, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.agglomeration = *label_opt;
      }
      if (descr.service.size()) {
        auto label_opt = GetFilteredLabel("service", descr.service, agg_rule);
        if (!label_opt) {
          continue;
        }
        descr.service = *label_opt;
      }
      descrs.push_back(descr);
    }
  } else {
    descrs.push_back(descr);
  }

  for (auto& descr : descrs) {
    labels0_percentile_container_.InsertThenUpdate(
        descr,
        [&value](bool, auto& counter) {
          counter.GetCurrentCounter().Add(value);
        }

    );
  }
}
void Writer::Invalidate() {
  empty_labels_milli_lap_container_.Clear();
  empty_labels_percentile_lap_container_.Clear();
  labels0_avg_counter_container_.Clear();
  labels0_counter_container_.Clear();
  labels0_milli_lap_container_.Clear();
  labels0_percentile_container_.Clear();
  labels1_time_counter_container_.Clear();
  labels1_time_percentile_container_.Clear();
}
}  // namespace metrix
