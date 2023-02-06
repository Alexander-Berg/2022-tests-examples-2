#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

#include <blocklist_predicate_evaluator/models/errors.hpp>
#include <blocklist_predicate_evaluator/models/predicate_evaluator.hpp>

namespace {
static const auto kCarNumberPredicate = "11111111-1111-1111-1111-111111111111";
static const auto kParkIdAndCarNumberPredicate =
    "22222222-2222-2222-2222-222222222222";

static const formats::json::Value condition_1 =
    formats::json::FromString(R"=({"type":"eq","value":"car_number"})=");

static const formats::json::Value condition_2 = formats::json::FromString(
    R"=({"type":"and","value":[{"type":"eq","value":"park_id"},{"type":"eq","value":"car_number"}]})=");

static const predicate_evaluator::RawPredicatesMap raw_predicates_map = {
    {kCarNumberPredicate, condition_1},
    {kParkIdAndCarNumberPredicate, condition_2}};

const auto kCarNumber = "car_number";
const auto kParkId = "park_id";
const auto kExtraKwarg = "extra_id";

const auto extra_1 = "extra_1";
const auto park_1 = "park_1";
const auto park_2 = "park_2";
const auto car_1 = "car_1";
const auto car_2 = "car_2";

}  // namespace

UTEST(BlocklistPredicateEvaluatorTest, PredicateProcessing) {
  predicate_evaluator::PredicateEvaluator evaluator;
  evaluator.Update(predicate_evaluator::RawPredicatesMap{raw_predicates_map});
  const auto park_and_car_pred_id =
      predicate_evaluator::PredicateWrapper::Parse(
          kParkIdAndCarNumberPredicate);
  const auto car_pred_id =
      predicate_evaluator::PredicateWrapper::Parse(kCarNumberPredicate);

  // process block and driver with equal kwargs
  predicate_evaluator::Map driver_kwargs = {{kParkId, park_1},
                                            {kCarNumber, car_1}};
  predicate_evaluator::Map block_kwargs = {{kParkId, park_1},
                                           {kCarNumber, car_1}};

  auto result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, true);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, true);

  // process block and driver with different park_id
  // but equal car_number
  driver_kwargs = {{kParkId, park_1}, {kCarNumber, car_1}};
  block_kwargs = {{kParkId, park_2}, {kCarNumber, car_1}};

  result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, true);

  // process block and driver with different park_id
  // and with different car_number
  driver_kwargs = {{kParkId, park_1}, {kCarNumber, car_1}};
  block_kwargs = {{kParkId, park_2}, {kCarNumber, car_2}};

  result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);

  // process driver with unknown extra kwarg and equal car_number
  // with different park_id
  driver_kwargs = {
      {kExtraKwarg, extra_1}, {kParkId, park_1}, {kCarNumber, car_1}};
  block_kwargs = {{kParkId, park_2}, {kCarNumber, car_1}};

  result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, true);

  // process block with unknown extra kwarg and equal car_number
  // with different park_id
  driver_kwargs = {{kParkId, park_1}, {kCarNumber, car_1}};
  block_kwargs = {
      {kExtraKwarg, extra_1}, {kParkId, park_2}, {kCarNumber, car_1}};

  result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, true);

  // process driver with missing park_id
  // and with equal car_number
  driver_kwargs = {{kCarNumber, car_1}};
  block_kwargs = {{kParkId, park_2}, {kCarNumber, car_1}};

  result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, true);

  // process empty block
  driver_kwargs = {{kParkId, park_2}, {kCarNumber, car_1}};
  block_kwargs = {};

  result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);

  // process empty driver
  driver_kwargs = {};
  block_kwargs = {{kParkId, park_2}, {kCarNumber, car_1}};

  result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);

  // process empty block and driver
  driver_kwargs = {};
  block_kwargs = {};

  result =
      evaluator.Evaluate(park_and_car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
  result = evaluator.Evaluate(car_pred_id, driver_kwargs, block_kwargs);
  EXPECT_EQ(result, false);
}

UTEST(BlocklistPredicateEvaluatorTest, PredicatesSpelling) {
  predicate_evaluator::PredicateEvaluator evaluator;
  const auto new_predicate_name = "55555555-5555-5555-5555-555555555555";

  // missing predicate type field
  {
    const formats::json::Value incorrect_condition =
        formats::json::FromString(R"=({"value":"car_number"})=");
    predicate_evaluator::RawPredicatesMap predicates_map = {
        {new_predicate_name, incorrect_condition}};
    bool exception_occured = false;
    try {
      evaluator.Update(std::move(predicates_map));
    } catch (const predicate_evaluator::IncorrectPredicateError& error) {
      EXPECT_EQ(true, true);
      exception_occured = true;
    } catch (const std::exception& e) {
      EXPECT_EQ(false, true);
      exception_occured = true;
    }
    EXPECT_EQ(exception_occured, true);
  }

  // missing predicate value field
  {
    const formats::json::Value incorrect_condition =
        formats::json::FromString(R"=({"type":"eq"})=");
    predicate_evaluator::RawPredicatesMap predicates_map = {
        {new_predicate_name, incorrect_condition}};
    bool exception_occured = false;
    try {
      evaluator.Update(std::move(predicates_map));
    } catch (const predicate_evaluator::IncorrectPredicateError& error) {
      EXPECT_EQ(true, true);
      exception_occured = true;
    } catch (const std::exception& e) {
      EXPECT_EQ(false, true);
      exception_occured = true;
    }
    EXPECT_EQ(exception_occured, true);
  }

  // missing missing second value evement in logic predicates
  {
    const formats::json::Value incorrect_condition = formats::json::FromString(
        R"=({"type":"and","value":[{"type":"eq","value":"car_number"}]})=");
    predicate_evaluator::RawPredicatesMap predicates_map = {
        {new_predicate_name, incorrect_condition}};
    bool exception_occured = false;
    try {
      evaluator.Update(std::move(predicates_map));
    } catch (const predicate_evaluator::IncorrectPredicateError& error) {
      EXPECT_EQ(true, true);
      exception_occured = true;
    } catch (const std::exception& e) {
      EXPECT_EQ(false, true);
      exception_occured = true;
    }
    EXPECT_EQ(exception_occured, true);
  }
}

UTEST(BlocklistPredicateEvaluatorTest, BasePredicatesCheck) {
  predicate_evaluator::PredicateEvaluator evaluator;
  const auto new_predicate_name = "55555555-5555-5555-5555-555555555555";
  const auto new_predicate_id =
      predicate_evaluator::PredicateWrapper::Parse(new_predicate_name);
  // correct EQ predicate
  {
    predicate_evaluator::RawPredicatesMap predicates_map = {
        {new_predicate_name, condition_1}};
    try {
      evaluator.Update(std::move(predicates_map));
    } catch (const std::exception& e) {
      EXPECT_EQ(false, true);
    }
    // process block and driver with equal kwargs
    {
      const predicate_evaluator::Map driver_kwargs = {
          {kCarNumber, "new_kwarg_1"}};
      const predicate_evaluator::Map block_kwargs = {
          {kCarNumber, "new_kwarg_1"}};

      auto result =
          evaluator.Evaluate(new_predicate_id, driver_kwargs, block_kwargs);
      EXPECT_EQ(result, true);
    }
    // process block and driver with different kwargs
    {
      const predicate_evaluator::Map driver_kwargs = {
          {kCarNumber, "new_kwarg_1"}};
      const predicate_evaluator::Map block_kwargs = {
          {kCarNumber, "new_kwarg_2"}};

      auto result =
          evaluator.Evaluate(new_predicate_id, driver_kwargs, block_kwargs);
      EXPECT_EQ(result, false);
    }
  }

  // correct AND predicate
  {
    predicate_evaluator::RawPredicatesMap predicates_map = {
        {new_predicate_name, condition_2}};
    try {
      evaluator.Update(std::move(predicates_map));
    } catch (const std::exception& e) {
      EXPECT_EQ(false, true);
    }
    // process block and driver with equal kwargs
    {
      const predicate_evaluator::Map driver_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_1"}};
      const predicate_evaluator::Map block_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_1"}};

      auto result =
          evaluator.Evaluate(new_predicate_id, driver_kwargs, block_kwargs);
      EXPECT_EQ(result, true);
    }
    // process block and driver with different kwargs
    {
      const predicate_evaluator::Map driver_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_1"}};
      const predicate_evaluator::Map block_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_2"}};

      auto result =
          evaluator.Evaluate(new_predicate_id, driver_kwargs, block_kwargs);
      EXPECT_EQ(result, false);
    }
  }

  // correct OR predicate
  {
    const formats::json::Value or_condition = formats::json::FromString(
        R"=({"type":"or","value":[{"type":"eq","value":"park_id"},{"type":"eq","value":"car_number"}]})=");
    predicate_evaluator::RawPredicatesMap predicates_map = {
        {new_predicate_name, or_condition}};
    try {
      evaluator.Update(std::move(predicates_map));
    } catch (const std::exception& e) {
      EXPECT_EQ(false, true);
    }
    // process block and driver with equal kwargs
    {
      const predicate_evaluator::Map driver_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_1"}};
      const predicate_evaluator::Map block_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_1"}};

      auto result =
          evaluator.Evaluate(new_predicate_id, driver_kwargs, block_kwargs);
      EXPECT_EQ(result, true);
    }
    // process block and driver with one pair of different kwargs
    {
      const predicate_evaluator::Map driver_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_1"}};
      const predicate_evaluator::Map block_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_2"}};

      auto result =
          evaluator.Evaluate(new_predicate_id, driver_kwargs, block_kwargs);
      EXPECT_EQ(result, true);
    }
    // process block and driver with another pair of different kwargs
    {
      const predicate_evaluator::Map driver_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_1"}};
      const predicate_evaluator::Map block_kwargs = {
          {kCarNumber, "new_kwarg_2"}, {kParkId, "park_1"}};

      auto result =
          evaluator.Evaluate(new_predicate_id, driver_kwargs, block_kwargs);
      EXPECT_EQ(result, true);
    }
    // process block and driver with two pair of different kwargs
    {
      const predicate_evaluator::Map driver_kwargs = {
          {kCarNumber, "new_kwarg_1"}, {kParkId, "park_1"}};
      const predicate_evaluator::Map block_kwargs = {
          {kCarNumber, "new_kwarg_2"}, {kParkId, "park_2"}};

      auto result =
          evaluator.Evaluate(new_predicate_id, driver_kwargs, block_kwargs);
      EXPECT_EQ(result, false);
    }
  }
}
