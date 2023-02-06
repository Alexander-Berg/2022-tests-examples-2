#pragma once

#include <clients/pricing-modifications-validator/client_fwd.hpp>
#include <clients/taxi-approvals/client_fwd.hpp>
#include <defs/definitions.hpp>
#include <interpreter/interpreter.hpp>
#include <pricing-components/defs/definitions/composite_price.hpp>
#include <pricing-components/defs/definitions/errors.hpp>
#include <pricing-extended/defs/definitions.hpp>
#include <pricing-extended/defs/definitions/rules.hpp>
#include <pricing-functions/lang/backend_variables.hpp>
#include <pricing-functions/lang/models/features.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/storages/postgres/cluster.hpp>

namespace helpers {

struct PriceConversionRunOutput {
  price_calc::models::Price price;
  std::unordered_map<std::string, double> metadata;
  std::optional<std::unordered_map<std::string, double>> interpreter_metadata;
};

struct InterpreterRunResult {
  bool success = false;
  std::optional<PriceConversionRunOutput> output;
  std::optional<std::string> error_message;
  std::vector<int> visited_lines;
};

struct PriceConversionRunResult : public InterpreterRunResult {
  handlers::RuleExecutionInfo execution_info;
};

PriceConversionRunResult RunPriceConversion(
    const price_calc::models::Price& initial_price,
    const price_calc::interpreter::TripDetails& trip_details,
    const lang::variables::BackendVariables& backend_variables,
    const lang::models::FeaturesSet& features, const std::string& source_code,
    const std::vector<std::string>& extra_return,
    const dynamic_config::Snapshot& config);

price_calc::models::Price Convert(
    const handlers::libraries::pricing_components::CompositePrice& price);

PriceConversionRunResult RunPriceConversion(
    const handlers::libraries::pricing_extended::RuleTest& test,
    const std::string& source_code,
    const std::vector<std::string>& extra_return,
    const dynamic_config::Snapshot& config);

std::optional<handlers::libraries::pricing_components::BadRequestError>
ValidateTestData(const handlers::libraries::pricing_extended::RuleTest& test);

std::pair<bool, std::optional<std::string>> VerifyRunResults(
    const helpers::PriceConversionRunOutput& run_result,
    const ::std::optional<
        ::handlers::libraries::pricing_components::CompositePrice>&
        expected_price,
    const ::std::optional<
        ::handlers::libraries::pricing_extended::CompilerMetadata>&
        expected_meta);

price_calc::models::Price RoundPriceComponents(
    const price_calc::models::Price& price);

struct RuleData {
  std::string name;
  int64_t id;
  std::string source;
  std::vector<std::string> extra_return;

  RuleData(const storages::postgres::ClusterPtr& cluster,
           const std::string& rule_name, const std::optional<int64_t>& rule_id,
           const std::optional<std::string>& source,
           const dynamic_config::Snapshot& config,
           const clients::taxi_approvals::Client& approvals_client,
           const clients::pricing_modifications_validator::Client& pmv_client);

  RuleData(const storages::postgres::ClusterPtr& cluster, const int64_t rule_id,
           const std::optional<std::string>& source);
};

struct MetaComparasionDiff {
  std::vector<std::string> differs;
  std::vector<std::string> exceed_in_expected;
  std::vector<std::string> exceed_in_result;
};

std::optional<MetaComparasionDiff> MakeMetaDiff(
    const std::unordered_map<std::string, double>& result_meta,
    const std::unordered_map<std::string, double>& expected_meta);

}  // namespace helpers
