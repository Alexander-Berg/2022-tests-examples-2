#include <views/v1/testing/test/put/view.hpp>

#include <boost/range/size.hpp>
#include <clients/pricing-modifications-validator/client.hpp>
#include <clients/taxi-approvals/client.hpp>
#include <helpers/approvals_request.hpp>
#include <helpers/price_conversion_test_run.hpp>
#include <interpreter/interpreter.hpp>
#include <pricing-extended/schemas/price_modifications.hpp>
#include <pricing-functions/helpers/price_calc_io.hpp>
#include <psql/execute.hpp>
#include <psql/query/any.hpp>
#include <psql/query/in.hpp>
#include <psql/query/insert.hpp>
#include <psql/query/operators.hpp>
#include <psql/query/select.hpp>
#include <userver/logging/log.hpp>
#include <userver/storages/postgres/cluster_types.hpp>

namespace {
namespace pm = price_modifications;

const auto kRuleById =
    psql::Select(pm::rules.source_code, pm::rules.name, pm::rules.extra_return)
        .From(pm::rules)
        .Where(pm::rules.rule_id == psql::_1);

const auto kRuleByRuleName =
    psql::Select(pm::rules.source_code, pm::rules.rule_id,
                 pm::rules.extra_return)
        .From(pm::rules, psql::kOnly)
        .Where((pm::rules.name == psql::_1) &&
               (pm::rules.deleted == std::false_type{}));

const std::vector<handlers::libraries::pricing_extended::RuleDraftA1Status>
    kDraftOkStatuses = {
        handlers::libraries::pricing_extended::RuleDraftA1Status::kToApprove,
        handlers::libraries::pricing_extended::RuleDraftA1Status::kRunning,
        handlers::libraries::pricing_extended::RuleDraftA1Status::kNotStarted,
        handlers::libraries::pricing_extended::RuleDraftA1Status::kSuccess};

const auto kDraftsByName =
    psql::Select(pm::rules_drafts.source_code, pm::rules_drafts.rule_id,
                 pm::rules_drafts.extra_return, pm::rules_drafts.author,
                 pm::rules_drafts.errors, pm::rules_drafts.approvals_id,
                 pm::rules_drafts.pmv_task_id)
        .From(pm::rules_drafts)
        .Where((pm::rules_drafts.name == psql::_1));

const auto kInsertTest =
    psql::InsertInto(pm::tests)(
        pm::tests.test_name, pm::tests.rule_name, pm::tests.backend_variables,
        pm::tests.trip_details, pm::tests.initial_price, pm::tests.output_price,
        pm::tests.output_meta, pm::tests.last_result,
        pm::tests.last_result_rule_id, pm::tests.price_calc_version)
        .OnConflict(pm::tests.rule_name, pm::tests.test_name)
        .DoUpdateSet(pm::tests.backend_variables = psql::_3,
                     pm::tests.trip_details = psql::_4,
                     pm::tests.initial_price = psql::_5,
                     pm::tests.output_price = psql::_6,
                     pm::tests.output_meta = psql::_7,
                     pm::tests.last_result = psql::_8,
                     pm::tests.last_result_rule_id = psql::_9,
                     pm::tests.price_calc_version = psql::_10);

struct RuleInfo {
  std::string rule_name;
  std::int64_t rule_id;
  std::string source_code;
  std::vector<std::string> extra_return;
};

struct RuleTestStatus {
  std::int64_t rule_id;
  bool success;
};

template <typename Range>
std::optional<typename boost::range_value<Range>::type> Single(
    const Range& range) {
  switch (boost::size(range)) {
    case 0u:
      return std::nullopt;
    default:
      return *range.begin();
  }
}

std::optional<RuleInfo> FetchRuleInfo(
    const std::shared_ptr<storages::postgres::Cluster>& cluster,
    const std::string& rule_name, std::optional<std::int64_t> rule_id,
    const dynamic_config::Snapshot& config,
    const clients::taxi_approvals::Client& approvals_client,
    const clients::pricing_modifications_validator::Client& pmv_client) {
  if (rule_id.has_value()) {
    const auto& rule = Single(psql::Execute(cluster, kRuleById, *rule_id));
    if (rule.has_value()) {
      return {{rule->name, *rule_id, rule->source_code, rule->extra_return}};
    }
  }

  const auto draft = Single(psql::Execute(cluster, kDraftsByName, rule_name));

  if (draft.has_value()) {
    if (helpers::approvals::CheckRuleDraftHasOkStatus(
            config, approvals_client, pmv_client, draft->rule_id, draft->author,
            draft->errors, draft->approvals_id, draft->pmv_task_id,
            kDraftOkStatuses)) {
      return {
          {rule_name, draft->rule_id, draft->source_code, draft->extra_return}};
    }
  }

  const auto rule = Single(psql::Execute(cluster, kRuleByRuleName, rule_name));
  if (rule.has_value()) {
    return {{rule_name, rule->rule_id, rule->source_code, rule->extra_return}};
  }
  return std::nullopt;
}

bool RunTest(const RuleInfo& rule_info,
             const handlers::libraries::pricing_extended::RuleTest& test,
             const dynamic_config::Snapshot& config) {
  auto run_result = helpers::RunPriceConversion(test, rule_info.source_code,
                                                rule_info.extra_return, config);

  if (run_result.error_message.has_value()) {
    LOG_WARNING() << "Run test error message: " << *run_result.error_message;
  }
  if (!run_result.success || !run_result.output) return false;

  const auto& [result, error_message] = helpers::VerifyRunResults(
      *run_result.output, test.output_price, test.output_meta);

  if (error_message.has_value()) {
    LOG_WARNING() << "Verify results test error message: " << *error_message;
    if (!run_result.error_message) {
      run_result.error_message = error_message;
    }
  }

  return result;
}

void InsertTest(const std::shared_ptr<storages::postgres::Cluster>& cluster,
                const std::string& test_name, const std::string& rule_name,
                const handlers::libraries::pricing_extended::RuleTest& test,
                const std::optional<RuleTestStatus>& test_result) {
  std::optional<bool> last_result;
  std::optional<std::int64_t> last_result_rule_id;
  if (test_result.has_value()) {
    last_result = test_result->success;
    last_result_rule_id = test_result->rule_id;
  }
  psql::Execute(cluster, kInsertTest, test_name, rule_name,
                test.backend_variables.extra,
                Serialize(test.trip_details,
                          formats::serialize::To<formats::json::Value>{}),
                Serialize(test.initial_price,
                          formats::serialize::To<formats::json::Value>{}),
                Serialize(test.output_price,
                          formats::serialize::To<formats::json::Value>{}),
                Serialize(test.output_meta,
                          formats::serialize::To<formats::json::Value>{}),
                last_result, last_result_rule_id, test.price_calc_version);
}

}  // namespace

namespace handlers::v1_testing_test::put {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  const auto& cluster = dependencies.pg_pricing_data_preparer->GetCluster();

  if (auto error = helpers::ValidateTestData(request.body.test);
      error.has_value())
    return Response400{std::move(*error)};

  std::optional<RuleTestStatus> test_result;
  auto rule_info =
      FetchRuleInfo(cluster, request.rule_name, request.body.rule_id,
                    dependencies.config, dependencies.taxi_approvals_client,
                    dependencies.pricing_modifications_validator_client);
  if (rule_info.has_value()) {
    if (rule_info->rule_name != request.rule_name)
      return Response400{
          {libraries::pricing_components::BadRequestCode::kInvalidParameters,
           "Rule from rule id differs from rule name"}};
    test_result.emplace(RuleTestStatus{
        rule_info->rule_id,
        RunTest(*rule_info, request.body.test, dependencies.config)});
  }

  InsertTest(cluster, request.test_name, request.rule_name, request.body.test,
             test_result);

  return response;
}

}  // namespace handlers::v1_testing_test::put
