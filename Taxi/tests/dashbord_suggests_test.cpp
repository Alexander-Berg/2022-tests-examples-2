#include <components/dashboard_suggests.hpp>

#include <defs/definitions.hpp>
#include <experiments3_common/models/predicates.hpp>
#include <taxi_config/taxi_config.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

#define ADD_KWARG(field)                 \
  if (suggests_values.field.has_value()) \
  kwargs.Update(#field, *suggests_values.field)

namespace eats_report_storage::utils {

::experiments3::models::KwargsMap GetKwargsMap(
    const types::SuggestValuesOpt& suggests_values) {
  ::experiments3::models::KwargsMap kwargs;
  ADD_KWARG(name);
  ADD_KWARG(address);
  ADD_KWARG(rating);
  ADD_KWARG(orders);
  ADD_KWARG(avg_check);
  ADD_KWARG(cancel_rating);
  ADD_KWARG(pict_share);
  ADD_KWARG(plus_flg);
  ADD_KWARG(dish_as_gift_flg);
  ADD_KWARG(discount_flg);
  ADD_KWARG(second_for_free_flg);
  ADD_KWARG(pickup_flg);
  ADD_KWARG(mercury_flg);
  return kwargs;
}

TEST(
    CheckSuggestParams,
    function_return_true_if_all_conditions_is_true_and_predicate_type_is_all_of) {
  auto params = formats::json::FromString(R"(
    {
      "init": {
        "predicates": [
          {
            "init": {
              "value": 1,
              "arg_name": "rating",
              "arg_type": "double"
            },
            "type": "gt"
          },
          {
            "init": {
              "value": true,
              "arg_name": "plus_flg",
              "arg_type": "bool"
            },
            "type": "eq"
          }
        ]
      },
      "type": "all_of"
    }
  )");
  types::SuggestValuesOpt suggest_values = {types::PlaceId{1},
                                            1,
                                            "name1",
                                            "address1",
                                            1.1,
                                            1,
                                            1,
                                            1.1,
                                            1.1,
                                            true,
                                            true,
                                            true,
                                            false,
                                            false,
                                            true};
  eats_report_storage::components::DashboardSuggestsComponentImpl impl;
  const auto kwargs = GetKwargsMap(suggest_values);
  const auto check = impl.CheckPredicates(params, kwargs);
  ASSERT_TRUE(check);
}

TEST(
    CheckSuggestParams,
    function_return_false_if_all_conditions_is_false_and_predicate_type_is_any_of) {
  auto params = formats::json::FromString(R"(
    {
      "init": {
        "predicates": [
          {
            "init": {
              "value": 2,
              "arg_name": "rating",
              "arg_type": "double"
            },
            "type": "gt"
          },
          {
            "init": {
              "value": false,
              "arg_name": "plus_flg",
              "arg_type": "bool"
            },
            "type": "eq"
          }
        ]
      },
      "type": "any_of"
    }
  )");
  types::SuggestValuesOpt suggest_values = {types::PlaceId{1},
                                            1,
                                            "name1",
                                            "address1",
                                            1.1,
                                            1,
                                            1,
                                            1.1,
                                            1.1,
                                            true,
                                            true,
                                            true,
                                            false,
                                            false,
                                            true};
  eats_report_storage::components::DashboardSuggestsComponentImpl impl;
  const auto kwargs = GetKwargsMap(suggest_values);
  const auto check = impl.CheckPredicates(params, kwargs);
  ASSERT_FALSE(check);
}

TEST(
    CheckSuggestParams,
    function_return_false_if_not_all_conditions_is_true_and_predicate_type_is_all_of) {
  auto params = formats::json::FromString(R"(
    {
      "init": {
        "predicates": [
          {
            "init": {
              "value": 1,
              "arg_name": "rating",
              "arg_type": "double"
            },
            "type": "gt"
          },
          {
            "init": {
              "value": true,
              "arg_name": "plus_flg",
              "arg_type": "bool"
            },
            "type": "eq"
          }
        ]
      },
      "type": "all_of"
    }
  )");
  types::SuggestValuesOpt suggest_values = {types::PlaceId{1},
                                            1,
                                            "name1",
                                            "address1",
                                            0.5,
                                            1,
                                            1,
                                            1.1,
                                            1.1,
                                            true,
                                            true,
                                            true,
                                            false,
                                            false,
                                            true};
  eats_report_storage::components::DashboardSuggestsComponentImpl impl;
  const auto kwargs = GetKwargsMap(suggest_values);
  const auto check = impl.CheckPredicates(params, kwargs);
  ASSERT_FALSE(check);
}

TEST(
    CheckSuggestParams,
    function_return_true_if_not_all_conditions_is_false_and_predicate_type_is_any_of) {
  auto params = formats::json::FromString(R"(
    {
      "init": {
        "predicates": [
          {
            "init": {
              "value": 1,
              "arg_name": "rating",
              "arg_type": "double"
            },
            "type": "gt"
          },
          {
            "init": {
              "value": true,
              "arg_name": "plus_flg",
              "arg_type": "bool"
            },
            "type": "eq"
          }
        ]
      },
      "type": "any_of"
    }
  )");
  types::SuggestValuesOpt suggest_values = {types::PlaceId{1},
                                            1,
                                            "name1",
                                            "address1",
                                            0.5,
                                            1,
                                            1,
                                            1.1,
                                            1.1,
                                            true,
                                            true,
                                            true,
                                            false,
                                            false,
                                            true};
  eats_report_storage::components::DashboardSuggestsComponentImpl impl;
  const auto kwargs = GetKwargsMap(suggest_values);
  const auto check = impl.CheckPredicates(params, kwargs);
  ASSERT_TRUE(check);
}

}  // namespace eats_report_storage::utils
