#include "view.hpp"

#include <helpers/db_rules.hpp>
#include <helpers/price_conversion_test_run.hpp>
#include <pricing-extended/helpers/definitions_converters.hpp>
#include <utils/epsilon_neighborhood.hpp>

#include <userver/logging/log.hpp>

namespace {

handlers::libraries::pricing_extended::RuleTest GetRuleTest(
    handlers::v1_testing_test::post::Request&& request,
    const storages::postgres::ClusterPtr& cluster, bool& loaded_from_db) {
  loaded_from_db = false;
  if (request.body.test_data) return std::move(*request.body.test_data);

  const auto& test = db::helpers::GetTestForRule(cluster, request.rule_name,
                                                 request.test_name);
  if (!test)
    throw handlers::v1_testing_test::post::Response404{
        {handlers::libraries::pricing_components::NotFoundCode::kTestNotFound,
         "Test for rule was not found"}};
  loaded_from_db = true;
  return static_cast<handlers::libraries::pricing_extended::RuleTest>(*test);
}

handlers::v1_testing_test::post::Response200 ErrorResponse200(
    const std::string& error) {
  return {false, error, {}, {}, {}, {}, {}, {}};
}
static const std::string kBoarding = "boarding";
static const std::string kDistance = "distance";
static const std::string kTime = "time";
static const std::string kWaiting = "waiting";
static const std::string kRequirements = "requirements";
static const std::string kTransitWaiting = "transit_waiting";
static const std::string kDestinationWaiting = "destination_waiting";

struct Lighting {
  std::vector<std::string> price;
  std::vector<std::string> metadata;

  Lighting(const helpers::PriceConversionRunOutput& run_result,
           const ::std::optional<
               ::handlers::libraries::pricing_components::CompositePrice>&
               expected_price,
           const ::std::optional<
               ::handlers::libraries::pricing_extended::CompilerMetadata>&
               expected_meta) {
    const auto& check = [](double x) {
      return utils::InEpsilonNeighborhoodOfZero(x);
    };
    if (expected_price) {
      const auto& output_price =
          ::helpers::RoundPriceComponents(run_result.price);
      const auto& expected_round = ::helpers::RoundPriceComponents(
          helpers::FromGenerated(*expected_price));
      if (!check(output_price.boarding - expected_round.boarding))
        price.push_back(kBoarding);
      if (!check(output_price.distance - expected_round.distance))
        price.push_back(kDistance);
      if (!check(output_price.time - expected_round.time))
        price.push_back(kTime);
      if (!check(output_price.waiting - expected_round.waiting))
        price.push_back(kWaiting);
      if (!check(output_price.requirements - expected_round.requirements))
        price.push_back(kRequirements);
      if (!check(output_price.transit_waiting - expected_round.transit_waiting))
        price.push_back(kTransitWaiting);
      if (!check(output_price.destination_waiting -
                 expected_round.destination_waiting))
        price.push_back(kDestinationWaiting);
    }

    if (expected_meta) {
      if (auto meta_diff =
              helpers::MakeMetaDiff(run_result.metadata, expected_meta->extra);
          meta_diff.has_value()) {
        metadata.insert(metadata.end(),
                        std::make_move_iterator(meta_diff->differs.begin()),
                        std::make_move_iterator(meta_diff->differs.end()));
        metadata.insert(
            metadata.end(),
            std::make_move_iterator(meta_diff->exceed_in_expected.begin()),
            std::make_move_iterator(meta_diff->exceed_in_expected.end()));
        metadata.insert(
            metadata.end(),
            std::make_move_iterator(meta_diff->exceed_in_result.begin()),
            std::make_move_iterator(meta_diff->exceed_in_result.end()));
      }
    }
  }
};

}  // namespace

namespace handlers::v1_testing_test::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto cluster = dependencies.pg_pricing_data_preparer->GetCluster();

  std::optional<helpers::RuleData> rule_opt;
  try {
    rule_opt.emplace(cluster, request.rule_name, request.body.rule_id,
                     request.body.source, dependencies.config,
                     dependencies.taxi_approvals_client,
                     dependencies.pricing_modifications_validator_client);
  } catch (const std::logic_error& er) {
    return Response400{
        {libraries::pricing_components::BadRequestCode::kInvalidParameters,
         er.what()}};
  } catch (const std::invalid_argument& er) {
    return Response404{
        {libraries::pricing_components::NotFoundCode::kRuleNotFound,
         er.what()}};
  }
  if (!rule_opt) {
    return Response400{
        {libraries::pricing_components::BadRequestCode::kInvalidParameters,
         "Can't fetch rule for unknown reason"}};
  }
  const auto& rule = *rule_opt;

  bool test_loaded_from_db = false;
  const auto test_name = request.test_name;
  const auto& test =
      GetRuleTest(std::move(request), cluster, test_loaded_from_db);
  const auto& check_test = helpers::ValidateTestData(test);
  if (check_test)
    return ErrorResponse200("Incorrect test data: " + check_test->message);

  const auto& run_result = helpers::RunPriceConversion(
      test, rule.source, rule.extra_return, dependencies.config);

  if (!run_result.success || !run_result.output) {
    if (test_loaded_from_db) {
      db::helpers::SaveTestResult(cluster, rule.name, test_name,
                                  {false, rule.id, run_result.visited_lines});
    }
    return ErrorResponse200(run_result.error_message.value_or("no message"));
  }

  const auto& [verify_result, verify_error_message] =
      VerifyRunResults(*run_result.output, test.output_price, test.output_meta);
  if (verify_error_message) {
    LOG_WARNING() << "Verify errors: " << *verify_error_message;
  }

  Response200 response;
  response.result = verify_result;
  response.visited_lines = run_result.visited_lines;
  if (run_result.error_message) {
    response.error.emplace("Run errors: " + *run_result.error_message + "; ");
  }
  response.output_price = helpers::ToGenerated(run_result.output->price);
  if (!run_result.output->metadata.empty()) {
    response.metadata_map.emplace();
    response.metadata_map->extra = run_result.output->metadata;
  }

  if (!response.result) {
    Lighting lighting{*run_result.output, test.output_price, test.output_meta};
    if (!lighting.price.empty())
      response.output_price_lighting = lighting.price;
    if (!lighting.metadata.empty())
      response.metadata_lighting = lighting.metadata;
    if (!response.error) response.error.emplace();
    *response.error +=
        "Actual result Mismatches expected, check the result table";
  }

  if (test_loaded_from_db) {
    db::helpers::SaveTestResult(
        cluster, rule.name, test_name,
        {response.result, rule.id, response.visited_lines});
  }
  response.execution_statistic = run_result.execution_info;

  return response;
}

}  // namespace handlers::v1_testing_test::post
