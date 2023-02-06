#include <gtest/gtest.h>

#include <filters/efficiency/fetch_experiments/fetch_experiments.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utest/utest.hpp>

#include "fetch_experiment_classes.hpp"

namespace cf = candidates::filters;

namespace {

using Experiments = cf::efficiency::FetchExperimentClasses::Experiments;
using Experiment =
    experiments3::models::ClientsCache::MappedData::value_type::second_type;
using cf::efficiency::FetchExperimentClasses;

Experiment GetExperiment(const std::string& experiment_name, int value) {
  formats::json::ValueBuilder value_builder;
  value_builder["value"] = value;
  return Experiment{experiment_name, value_builder.ExtractValue(),
                    experiments3::models::ResultMetaInfo{0, 0, false}};
}

cf::Context GetContext(const Experiment& experiment) {
  cf::Context context;
  cf::efficiency::FetchExperiments::Set(context,
                                        {{experiment.name, experiment}});
  return context;
}

}  // namespace

UTEST(FetchExperimentClassesFilter, Basic) {
  const models::Classes allowed_classes{{"econom", "comfort", "vip"}};
  const models::Classes nomatch_classes{{"econom", "comfort"}};

  Experiment exp1 = GetExperiment("exp1", 1);
  Experiments user_experiments;
  user_experiments.emplace(exp1.name, exp1.value);

  const cf::FilterInfo kEmptyInfo;
  FetchExperimentClasses filter{kEmptyInfo,
                                allowed_classes,
                                {},
                                std::move(user_experiments),
                                nomatch_classes};
  {
    auto context = GetContext(exp1);
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
    EXPECT_EQ(allowed_classes, FetchExperimentClasses::Get(context));
  }
  {
    auto context = GetContext(GetExperiment("exp1", 2));
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
    EXPECT_EQ(nomatch_classes, FetchExperimentClasses::Get(context));
  }
  {
    auto context = GetContext(GetExperiment("exp1", 1));
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
    EXPECT_EQ(allowed_classes, FetchExperimentClasses::Get(context));
  }
  {
    auto context = GetContext(GetExperiment("exp2", 1));
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
    EXPECT_EQ(allowed_classes, FetchExperimentClasses::Get(context));
  }
}
