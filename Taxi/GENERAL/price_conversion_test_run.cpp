#include "price_conversion_test_run.hpp"

#include <fmt/format.h>

#include <boost/range/adaptor/filtered.hpp>
#include <boost/range/adaptor/map.hpp>
#include <boost/range/adaptor/transformed.hpp>

#include <clients/pricing-modifications-validator/client.hpp>
#include <clients/taxi-approvals/client.hpp>
#include <defs/definitions.hpp>
#include <helpers/approvals_request.hpp>
#include <helpers/metadata_mapping.hpp>
#include <pricing-components/helpers/metadata_mapping.hpp>
#include <pricing-components/helpers/price_detailing.hpp>
#include <pricing-components/utils/as.hpp>
#include <pricing-extended/helpers/definitions_converters.hpp>
#include <pricing-extended/schemas/price_modifications.hpp>
#include <pricing-functions/helpers/bv_optional_parse.hpp>
#include <pricing-functions/helpers/price_calc_io.hpp>
#include <pricing-functions/parser/ast_parser.hpp>
#include <psql/execute.hpp>
#include <psql/query/any.hpp>
#include <psql/query/operators.hpp>
#include <psql/query/select.hpp>
#include <taxi_config/taxi_config.hpp>
#include <userver/logging/log.hpp>
#include <userver/tracing/span.hpp>
#include <utils/verifications.hpp>

namespace {

const std::string kBoarding{"\'boarding\'"};
const std::string kDistance{"\'distance\'"};
const std::string kTime{"\'time\'"};
const std::string kWaiting{"\'waiting\'"};
const std::string kRequirements{"\'requirements\'"};
const std::string kTransitWaiting{"\'transit_waiting\'"};
const std::string kDestinationWaiting{"\'destination_waiting\'"};

const float kRound = 1e2;

double Round(const double x) { return std::round(x * kRound) / kRound; }

std::optional<std::string> CheckPriceComponentsForNan(
    price_calc::models::Price& price) {
  std::optional<std::string> ans = std::nullopt;
  if (std::isnan(price.boarding)) {
    ans =
        std::make_optional(ans ? (ans.value() + ", " + kBoarding) : kBoarding);
    price.boarding = 0;
  }
  if (std::isnan(price.distance)) {
    ans =
        std::make_optional(ans ? (ans.value() + ", " + kDistance) : kDistance);
    price.distance = 0;
  }
  if (std::isnan(price.time)) {
    ans = std::make_optional(ans ? (ans.value() + ", " + kTime) : kTime);
    price.time = 0;
  }
  if (std::isnan(price.waiting)) {
    ans = std::make_optional(ans ? (ans.value() + ", " + kWaiting) : kWaiting);
    price.waiting = 0;
  }
  if (std::isnan(price.requirements)) {
    ans = std::make_optional(ans ? (ans.value() + ", " + kRequirements)
                                 : kRequirements);
    price.requirements = 0;
  }
  if (std::isnan(price.transit_waiting)) {
    ans = std::make_optional(ans ? (ans.value() + ", " + kTransitWaiting)
                                 : kTransitWaiting);
    price.transit_waiting = 0;
  }
  if (std::isnan(price.destination_waiting)) {
    ans = std::make_optional(ans ? (ans.value() + ", " + kDestinationWaiting)
                                 : kDestinationWaiting);
    price.destination_waiting = 0;
  }

  return ans;
}

// first price is CalculateFix result, second price is RunBulk result
std::string PriceDifferenceToString(const price_calc::models::Price& lprice,
                                    const price_calc::models::Price& rprice) {
  std::string lstr =
      "{" + kBoarding + ": " + std::to_string(lprice.boarding) + ", " +
      kDistance + ": " + std::to_string(lprice.distance) + ", " + kTime + ": " +
      std::to_string(lprice.time) + ", " + kWaiting + ": " +
      std::to_string(lprice.waiting) + ", " + kRequirements + ": " +
      std::to_string(lprice.requirements) + ", " + kTransitWaiting + ": " +
      std::to_string(lprice.transit_waiting) + ", " + kDestinationWaiting +
      ": " + std::to_string(lprice.destination_waiting) + "}";
  std::string rstr =
      "{" + kBoarding + ": " + std::to_string(rprice.boarding) + ", " +
      kDistance + ": " + std::to_string(rprice.distance) + ", " + kTime + ": " +
      std::to_string(rprice.time) + ", " + kWaiting + ": " +
      std::to_string(rprice.waiting) + ", " + kRequirements + ": " +
      std::to_string(rprice.requirements) + ", " + kTransitWaiting + ": " +
      std::to_string(rprice.transit_waiting) + ", " + kDestinationWaiting +
      ": " + std::to_string(rprice.destination_waiting) + "}";
  return lstr + " != " + rstr;
}

bool CompareMeta(const std::unordered_map<std::string, double>& result_meta,
                 const std::unordered_map<std::string, double>& expected_meta,
                 const bool compare_size) {
  if (compare_size && (result_meta.size() != expected_meta.size())) {
    return false;
  }

  for (const auto& [meta_name, meta_value] : expected_meta) {
    if (const auto& res_meta = result_meta.find(meta_name);
        res_meta == result_meta.end() ||
        abs(res_meta->second - meta_value) >= 1. / kRound) {
      return false;
    }
  }

  return true;
}

bool CompareMetaStrict(
    const std::unordered_map<std::string, double>& result_meta,
    const std::unordered_map<std::string, double>& expected_meta) {
  const bool compare_size = true;
  return CompareMeta(result_meta, expected_meta, compare_size);
}

bool CompareMetaIdle(
    const std::optional<std::unordered_map<std::string, double>>& result_meta,
    const std::unordered_map<std::string, double>& expected_meta) {
  const bool compare_size = false;
  return (result_meta ? CompareMeta(*result_meta, expected_meta, compare_size)
                      : expected_meta.empty());
}

namespace pm = price_modifications;

const auto kRuleById =
    psql::Select(pm::rules.rule_id, pm::rules.name, pm::rules.source_code,
                 pm::rules.extra_return)
        .From(pm::rules)
        .Where(pm::rules.rule_id == psql::_1);

const std::vector<handlers::libraries::pricing_extended::RuleDraftA1Status>
    kDraftOkStatuses = {
        handlers::libraries::pricing_extended::RuleDraftA1Status::kToApprove,
        handlers::libraries::pricing_extended::RuleDraftA1Status::kRunning,
        handlers::libraries::pricing_extended::RuleDraftA1Status::kNotStarted,
        handlers::libraries::pricing_extended::RuleDraftA1Status::kSuccess};

const auto kDraftByName =
    psql::Select(pm::rules_drafts.rule_id, pm::rules_drafts.name,
                 pm::rules_drafts.source_code, pm::rules_drafts.extra_return,
                 pm::rules_drafts.author, pm::rules_drafts.errors,
                 pm::rules_drafts.approvals_id, pm::rules_drafts.pmv_task_id)
        .From(pm::rules_drafts, psql::kOnly)
        .Where(pm::rules_drafts.name == psql::_1);

const auto kRuleByName =
    psql::Select(pm::rules.rule_id, pm::rules.name, pm::rules.source_code,
                 pm::rules.extra_return)
        .From(pm::rules, psql::kOnly)
        .Where((pm::rules.name == psql::_1) &&
               (pm::rules.deleted == std::false_type{}));

struct InterpreterResultWithExecutionInfo : helpers::InterpreterRunResult {
  std::chrono::milliseconds interpretation_time{};
  size_t bytecode_size = 0;
};

InterpreterResultWithExecutionInfo MakeErrorResult(const std::string& message) {
  return {
      {false /* success */, {} /* output */, message, {} /* visited_lines */},
      {} /* interpretation_time */,
      0 /* bytecode_size */};
}

helpers::PriceConversionRunResult MakeInterpreterRunError(
    const std::string& message) {
  return {
      {false /* success */, {} /* output */, message, {} /* visited_lines */},
      {} /* execution_info */};
}

InterpreterResultWithExecutionInfo CompileAndRun(
    const lang::models::LinkedProgram& simplified_ast,
    const price_calc::models::Price& initial_price,
    const price_calc::interpreter::TripDetails& trip_details,
    const std::unordered_set<lang::meta_modifications::MetaId>&
        metadata_mapping) {
  price_calc::models::BinaryData compiled;
  auto& span = tracing::Span::CurrentSpan();
  auto scope = span.CreateScopeTime("compile_and_run_interpreter");
  lang::models::GlobalCompilationContext compilation_context{};
  try {
    compiled = simplified_ast.Compile(
        metadata_mapping, {true /* drop_empty_return */}, compilation_context);
  } catch (const std::exception& ex) {
    return MakeErrorResult(
        std::string{"Error while compilling simplified_ast: "} + ex.what());
  }

  InterpreterResultWithExecutionInfo result{{true, {}, {}, {}}};

  try {
    scope.Reset("run_iterpreter");
    result.bytecode_size = compiled.size();
    const auto int_metadata_mapping =
        As<std::unordered_map<std::string, int32_t>>(
            metadata_mapping | boost::adaptors::transformed([](const auto& kv) {
              return std::make_pair(kv.key, static_cast<int32_t>(kv.value));
            }));

    const auto& output = price_calc::interpreter::RunBulk(
        initial_price, trip_details,
        std::vector<uint8_t>(std::make_move_iterator(compiled.begin()),
                             std::make_move_iterator(compiled.end())),
        1.0, int_metadata_mapping);

    result.interpretation_time =
        std::chrono::duration_cast<std::chrono::milliseconds>(scope.Reset());
    std::string interpreter_errors;
    for (const auto& info : std::get<2>(output)) {
      if (info.error) {
        interpreter_errors += info.error.value() + ' ';
      }
    }
    if (!interpreter_errors.empty()) {
      return MakeErrorResult(std::string{"Interpreter finished with errors: "} +
                             interpreter_errors + '\n');
    }

    price_calc::models::Price interpreter_price = std::get<1>(output);
    const auto& nan_param = CheckPriceComponentsForNan(interpreter_price);
    if (nan_param) {
      result.success = false;
      result.error_message = result.error_message.value_or("") +
                             "Interpreter price component(s) " +
                             nan_param.value() +
                             " is(are) nan in interpreter result.\n";
    }

    const auto inverted_taximeter_map =
        As<std::unordered_map<uint16_t, std::string>>(
            metadata_mapping | boost::adaptors::transformed([](const auto& kv) {
              return std::make_pair(kv.value, kv.key);
            }));

    const auto& interpreter_meta = std::get<3>(output);

    result.output = helpers::PriceConversionRunOutput{
        interpreter_price, interpreter_meta, interpreter_meta};

  } catch (const std::exception& ex) {
    result.success = false;
    result.error_message =
        result.error_message.value_or("") +
        "Error while running interpreter: " + std::string(ex.what()) + '\n';
  }
  return result;
}

std::string FormatMetaComparasionErrorText(
    const helpers::MetaComparasionDiff& diff) {
  return fmt::format(
      "differs: [{}], exceed in expected: [{}], exceed in result: [{}]",
      fmt::join(diff.differs, ","), fmt::join(diff.exceed_in_expected, ","),
      fmt::join(diff.exceed_in_result, ","));
}

template <typename T>
std::string MakeMetadataMappingLog(
    const std::unordered_map<std::string, T>& metadata_mapping) {
  return fmt::format(
      "{{{}}}",
      fmt::join(
          metadata_mapping | boost::adaptors::transformed([](const auto& item) {
            return fmt::format("{}: {}", item.first, item.second);
          }),
          ", "));
}

std::string MakeMetadataMappingLog(
    const std::unordered_set<lang::meta_modifications::MetaId>&
        metadata_mapping) {
  return fmt::format(
      "{{{}}}",
      fmt::join(
          metadata_mapping | boost::adaptors::transformed([](const auto& item) {
            return fmt::format("{}: {}", item.key, item.value);
          }),
          ", "));
}

}  // namespace

namespace helpers {

std::optional<MetaComparasionDiff> MakeMetaDiff(
    const std::unordered_map<std::string, double>& result_meta,
    const std::unordered_map<std::string, double>& expected_meta) {
  LOG_DEBUG() << "result meta: " << MakeMetadataMappingLog(result_meta);
  LOG_DEBUG() << "expected meta: " << MakeMetadataMappingLog(expected_meta);

  MetaComparasionDiff result{};
  auto count_absent = 0;
  const auto& check = [](double x) {
    return utils::InEpsilonNeighborhoodOfZero(x);
  };

  for (const auto& [name, value] : expected_meta) {
    if (const auto& emit = result_meta.find(name); emit != result_meta.end()) {
      if (!check(value - emit->second)) result.differs.push_back(name);
    } else {
      result.exceed_in_expected.push_back(name);
      ++count_absent;
    }
  }

  // for the case of excess meta in output
  if (result_meta.size() + count_absent > expected_meta.size()) {
    for (const auto& [name, _] : result_meta) {
      if (!expected_meta.count(name)) result.exceed_in_result.push_back(name);
    }
  }

  if (result.differs.empty() && result.exceed_in_expected.empty() &&
      result.exceed_in_result.empty())
    return {};

  return result;
}

PriceConversionRunResult RunPriceConversion(
    const price_calc::models::Price& initial_price,
    const price_calc::interpreter::TripDetails& trip_details,
    const lang::variables::BackendVariables& backend_variables,
    const lang::models::FeaturesSet& features, const std::string& source_code,
    [[maybe_unused]] const std::vector<std::string>& extra_return,
    const dynamic_config::Snapshot& config) {
  std::shared_ptr<lang::models::Program> ast;
  PriceConversionRunResult result{{true, {}, {}, {}}, {}};

  {
    handlers::libraries::pricing_extended::Rule test_rule;
    test_rule.name = tracing::Span::CurrentSpan().GetLink();
    test_rule.source_code = source_code;
    auto verification_result =
        utils::verifications::QuickCheck(test_rule, features, config);
    if (verification_result.status !=
        handlers::VerificationResultStatus::kSuccess) {
      return MakeInterpreterRunError(
          std::string{"Error while verification source_code: "} +
          verification_result.error_message.value_or("unknown"));
    }
    ast = verification_result.ast;
    result.execution_info.timings = verification_result.timings_info;
    result.execution_info.sizes.raw_ast =
        verification_result.serialized_ast.size();
  }

  const auto& lang_trip_details = lang::variables::TripDetails{
      trip_details.total_distance_,
      static_cast<double>(trip_details.total_time_.count())};

  std::unordered_map<std::string, double> driver_meta;

  lang::models::CalcResult calc_res_fix;
  price_calc::models::Price fix_price;

  try {
    calc_res_fix = ast->CalculateFix(
        backend_variables, lang_trip_details,
        {{static_cast<double>(trip_details.waiting_time_.count()),
          static_cast<double>(trip_details.waiting_in_transit_time_.count()),
          static_cast<double>(
              trip_details.waiting_in_destination_time_.count()),
          trip_details.user_options_, trip_details.user_meta_},
         initial_price},
        features, {}, true /* enable_debug */);

    driver_meta = calc_res_fix.metadata;

    fix_price = calc_res_fix.price;

    if (calc_res_fix.debug_info) {
      result.visited_lines.reserve(
          calc_res_fix.debug_info->visited_lines.size());
      std::copy(calc_res_fix.debug_info->visited_lines.begin(),
                calc_res_fix.debug_info->visited_lines.end(),
                std::back_inserter(result.visited_lines));
      std::sort(result.visited_lines.begin(), result.visited_lines.end());
    }

    const auto& nan_param = CheckPriceComponentsForNan(fix_price);
    if (nan_param) {
      result.success = false;
      result.error_message = result.error_message.value_or("") +
                             "Fixed price component(s) " + nan_param.value() +
                             " is(are) nan in interpreter result.";
    }
  } catch (const parser::AssertionError& error) {
    result.success = false;
    result.error_message = result.error_message.value_or("") +
                           "Assertion error: " + std::string(error.what());
  } catch (const std::exception& ex) {
    result.success = false;
    result.error_message =
        result.error_message.value_or("") +
        "Error while calculating fix_price: " + std::string(ex.what());
  }

  const auto& emitted_metadata_keys = As<std::unordered_set<std::string>>(
      driver_meta | boost::adaptors::map_keys);
  const auto& metadata_mapping =
      helpers::GetMetadataMappingForCompile(emitted_metadata_keys, config);

  LOG_DEBUG() << "CalculateFix metadata: "
              << MakeMetadataMappingLog(driver_meta);
  LOG_DEBUG() << "Metadata used to compile: "
              << MakeMetadataMappingLog(metadata_mapping.Get());

  std::optional<lang::models::LinkedProgram> simplified_ast;
  std::optional<lang::models::LinkedProgram> simplified_ast_fix;
  lang::models::GlobalLinkContext link_context{};
  lang::models::GlobalCompilationContext compilation_context{};
  try {
    simplified_ast =
        ast->Link(backend_variables, std::nullopt, features, link_context);
    simplified_ast_fix =
        ast->Link(backend_variables, std::make_optional(lang_trip_details),
                  features, link_context);
  } catch (const std::exception& ex) {
    return MakeInterpreterRunError(
        std::string{"Error while simplifying ast: "} + ex.what());
  }

  InterpreterResultWithExecutionInfo interpreter_result{};
  if (simplified_ast) {
    result.execution_info.sizes.simplified_ast_taximeter_price =
        simplified_ast->Serialize().size();
    interpreter_result = CompileAndRun(*simplified_ast, initial_price,
                                       trip_details, metadata_mapping.Get());
  }

  InterpreterResultWithExecutionInfo interpreter_result_fix{};
  if (simplified_ast_fix) {
    result.execution_info.sizes.simplified_ast_fix_price =
        simplified_ast_fix->Serialize().size();
    interpreter_result_fix =
        CompileAndRun(*simplified_ast_fix, initial_price, trip_details,
                      metadata_mapping.Get());
  }

  result.execution_info.sizes.bytecode_taximeter_price =
      interpreter_result.bytecode_size;
  result.execution_info.timings.bytecode_interpretation_taximeter_price =
      interpreter_result.interpretation_time;

  if (!interpreter_result.success) {
    return {interpreter_result, result.execution_info};
  }

  result.execution_info.sizes.bytecode_fix_price =
      interpreter_result.bytecode_size;
  result.execution_info.timings.bytecode_interpretation_fix_price =
      interpreter_result.interpretation_time;

  if (!interpreter_result_fix.success) {
    return {interpreter_result_fix, result.execution_info};
  }

  if (!interpreter_result.output.has_value() ||
      !interpreter_result_fix.output.has_value()) {
    return MakeInterpreterRunError(
        "Interpreter execution doesn't return prices");
  }

  const auto& interpreter_output = *interpreter_result.output;
  const auto& interpreter_output_fix = *interpreter_result_fix.output;

  const auto& interpreter_price = interpreter_output.price;
  const auto& interpreter_price_fix = interpreter_output_fix.price;

  if (interpreter_price != interpreter_price_fix) {
    return MakeInterpreterRunError(
        R"(In RunBulk result 'price' and 'fixed_price' are not equal: )" +
        PriceDifferenceToString(interpreter_price, interpreter_price_fix) +
        '\n');
  }

  LOG_DEBUG() << "MetaDiff interpreter & interpreter_fix";
  if (const auto& diff = MakeMetaDiff(interpreter_output.metadata,
                                      interpreter_output_fix.metadata);
      diff.has_value()) {
    return MakeInterpreterRunError(
        "Interpreter meta results for fix and taximeter are different: " +
        FormatMetaComparasionErrorText(*diff));
  }

  const auto& driver_meta_taximeter_only =
      As<std::unordered_map<std::string, double>>(
          driver_meta |
          boost::adaptors::filtered([&metadata_mapping](const auto& item) {
            return metadata_mapping.Get().count({{item.first}});
          }));
  LOG_DEBUG() << "MetaDiff driver_meta & interpreter";
  if (const auto& diff =
          MakeMetaDiff(driver_meta_taximeter_only, interpreter_output.metadata);
      diff.has_value()) {
    return MakeInterpreterRunError(
        "CalculateFix and RunBulk meta results are not equal: " +
        FormatMetaComparasionErrorText(*diff));
  }

  if (fix_price != interpreter_price) {
    result.success = false;
    result.error_message =
        result.error_message.value_or("") +
        "CalculateFix and RunBulk results are not equal: " +
        PriceDifferenceToString(fix_price, interpreter_price) + '\n';
  }

  if (result.success) {
    result.output =
        PriceConversionRunOutput{RoundPriceComponents(interpreter_price),
                                 driver_meta, interpreter_output.metadata};
  }
  return result;
}

PriceConversionRunResult RunPriceConversion(
    const handlers::libraries::pricing_extended::RuleTest& test,
    const std::string& source_code,
    const std::vector<std::string>& extra_return,
    const dynamic_config::Snapshot& config) {
  return RunPriceConversion(
      FromGenerated(test.initial_price),
      helpers::FromGenerated(test.trip_details),
      formats::parse::ParseBackendVariablesOptional(
          test.backend_variables.extra),
      lang::models::ListFeatures(test.price_calc_version.value_or("")),
      source_code, extra_return, config);
}

std::optional<handlers::libraries::pricing_components::BadRequestError>
ValidateTestData(const handlers::libraries::pricing_extended::RuleTest& test) {
  try {
    formats::parse::ParseBackendVariablesOptional(test.backend_variables.extra);
  } catch (const std::exception& e) {
    return {{handlers::libraries::pricing_components::BadRequestCode::
                 kInvalidParameters,
             std::string{"Invalid backend variable passed : "} + e.what()}};
  }
  return std::nullopt;
}

std::pair<bool, std::optional<std::string>> VerifyRunResults(
    const helpers::PriceConversionRunOutput& run_result,
    const ::std::optional<
        ::handlers::libraries::pricing_components::CompositePrice>&
        expected_price,
    const ::std::optional<
        ::handlers::libraries::pricing_extended::CompilerMetadata>&
        expected_meta) {
  bool res = true;
  std::optional<std::string> error_message;

  if (expected_price.has_value() &&
      RoundPriceComponents(run_result.price) !=
          RoundPriceComponents(helpers::FromGenerated(*expected_price))) {
    res = false;
    error_message = std::string{"Expected and result prices are not equal"};
  }

  if (res && expected_meta.has_value()) {
    res = CompareMetaStrict(run_result.metadata, expected_meta->extra);
    if (res) {
      if (!CompareMetaIdle(run_result.interpreter_metadata,
                           expected_meta->extra)) {
        error_message =
            std::string{"Interpreter metadata don't contain expected metadata"};
      }
    } else {
      error_message =
          std::string{"Result metadata don't contain expected metadata"};
    }
  }

  return std::make_pair(std::move(res), std::move(error_message));
}

RuleData::RuleData(
    const storages::postgres::ClusterPtr& cluster, const std::string& rule_name,
    const std::optional<int64_t>& rule_id,
    const std::optional<std::string>& source_code,
    const dynamic_config::Snapshot& config,
    const clients::taxi_approvals::Client& approvals_client,
    const clients::pricing_modifications_validator::Client& pmv_client)
    : name(rule_name) {
  if (rule_id) {
    id = *rule_id;
    const auto rules = psql::Execute(cluster, kRuleById, id);
    if (rules.empty()) throw std::invalid_argument{"Rule not found"};
    const auto& rule = rules.front();
    if (rule.name != rule_name)
      throw std::logic_error{"rule_id and rule_name mismatch"};
    source = source_code.value_or(rule.source_code);
    extra_return = rule.extra_return;
  } else {
    if (const auto drafts_result =
            psql::Execute(cluster, kDraftByName, rule_name);
        !drafts_result.empty() &&
        helpers::approvals::CheckRuleDraftHasOkStatus(
            config, approvals_client, pmv_client, drafts_result.front().rule_id,
            drafts_result.front().author, drafts_result.front().errors,
            drafts_result.front().approvals_id,
            drafts_result.front().pmv_task_id, kDraftOkStatuses)) {
      id = drafts_result.front().rule_id;
      source = source_code.value_or(drafts_result.front().source_code);
      extra_return = drafts_result.front().extra_return;
    } else if (const auto rules_result =
                   psql::Execute(cluster, kRuleByName, rule_name);
               !rules_result.empty()) {
      id = rules_result.front().rule_id;
      source = source_code.value_or(rules_result.front().source_code);
      extra_return = rules_result.front().extra_return;
    } else {
      throw std::invalid_argument{"Cannot run test without real rule"};
    }
  }
}

RuleData::RuleData(const storages::postgres::ClusterPtr& cluster,
                   const int64_t rule_id,
                   const std::optional<std::string>& source_code) {
  const auto rules = psql::Execute(cluster, kRuleById, rule_id);
  if (rules.empty()) throw std::invalid_argument{"Rule not found"};
  const auto& rule = rules.front();
  id = rule_id;
  name = rule.name;
  source = source_code.value_or(rule.source_code);
}

price_calc::models::Price RoundPriceComponents(
    const price_calc::models::Price& price) {
  return price_calc::models::Price(
      Round(price.boarding), Round(price.distance), Round(price.time),
      Round(price.waiting), Round(price.requirements),
      Round(price.transit_waiting), Round(price.destination_waiting));
}

}  // namespace helpers
