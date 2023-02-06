#include <gtest/gtest.h>

#include <filters/efficiency/fetch_experiments/fetch_experiments.hpp>
#include <userver/formats/json/value_builder.hpp>

#include "experiments_intersection.hpp"

namespace cf = candidates::filters;

namespace {
using Experiments = cf::efficiency::ExperimentsIntersection::Experiments;
using Experiment =
    experiments3::models::ClientsCache::MappedData::value_type::second_type;

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

TEST(ExperimentsIntersectionFilter, Basic) {
  Experiment exp1 = GetExperiment("exp1", 1);
  Experiments user_experiments;
  user_experiments.emplace(exp1.name, exp1.value);
  const cf::FilterInfo emptyInfo;
  cf::efficiency::ExperimentsIntersection filter{emptyInfo,
                                                 std::move(user_experiments)};
  {
    auto context = GetContext(exp1);
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  }
  {
    auto context = GetContext(GetExperiment("exp1", 2));
    EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);
  }
  {
    auto context = GetContext(GetExperiment("exp2", 1));
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  }
}
