#include <gtest/gtest.h>

#include <candidates/filters/test/dummy.hpp>
#include <filters/infrastructure/fetch_dbpark/fetch_dbpark_test.hpp>
#include <filters/infrastructure/fetch_driver_status/fetch_driver_status.hpp>
#include <filters/infrastructure/fetch_park/fetch_park.hpp>
#include <filters/infrastructure/park_id/park_id.hpp>
#include <filters/infrastructure/status/status.hpp>
#include <testing/taxi_config.hpp>

#include "any_of.hpp"

namespace cf = candidates::filters;
namespace cfi = candidates::filters::infrastructure;

namespace {

const cf::FilterInfo kAnyOfInfo = {"any_of", {}, {}, true, {}};
const cf::FilterInfo kEmptyInfo;

candidates::Environment CreateEnvironment() {
  return candidates::Environment(dynamic_config::GetDefaultSnapshot());
}

}  // namespace

TEST(AnyOf, Sample) {
  std::vector<std::unique_ptr<cf::Filter>> filters;
  cfi::Status::Params status_params{std::nullopt, true};
  filters.push_back(std::make_unique<cfi::Status>(kEmptyInfo, status_params));
  filters.push_back(std::make_unique<cfi::ParkId>(
      kEmptyInfo, std::unordered_set<std::string>{{"excluded"}}));
  filters.push_back(nullptr);

  cfi::AnyOf filter(kAnyOfInfo, std::move(filters));

  cf::Context context;
  cfi::FetchDriverStatus::Set(context, models::DriverStatus::kOnline);
  cfi::test::SetClid(context, "excluded");

  models::Park park;
  park.city = "wrong";
  cfi::FetchPark::Set(context, std::make_shared<models::Park>(park));

  // Status filter should allow
  EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);

  // Both filters should disallow
  cfi::FetchDriverStatus::Set(context, models::DriverStatus::kBusy);
  EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);

  // Park filter should allow
  cfi::test::SetClid(context, "allowed");
  EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
}

TEST(AnyOf, NullAndIgnore) {
  {
    std::vector<std::unique_ptr<cf::Filter>> filters;
    filters.push_back(nullptr);
    filters.push_back(std::make_unique<cf::test::IgnoreAll>(kEmptyInfo));
    filters.push_back(nullptr);

    cfi::AnyOf filter(kAnyOfInfo, std::move(filters));
    cf::Context context;
    EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);
  }
  {
    std::vector<std::unique_ptr<cf::Filter>> filters;
    filters.push_back(nullptr);
    filters.push_back(std::make_unique<cf::test::IgnoreAll>(kEmptyInfo));
    filters.push_back(nullptr);
    filters.push_back(std::make_unique<cf::test::AllowAll>(kEmptyInfo));

    cfi::AnyOf filter(kAnyOfInfo, std::move(filters));
    cf::Context context;
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  }
}

namespace candidates::filters::test {

class Repeat : public Filter {
 public:
  using Filter::Filter;

  Result Process([[maybe_unused]] const GeoMember& member,
                 Context& context) const override {
    const auto flag = flag_data_.Get(context, false);
    if (flag) return Result::kDisallow;
    return Result::kRepeat;
  }

  static void SetFlag(Context& context, bool flag) {
    flag_data_.Set(context, flag);
  }

 private:
  static const FilterData<Repeat, bool> flag_data_;
};

const FilterData<Repeat, bool> Repeat::flag_data_("flag");

class Counter : public Filter {
 public:
  Counter(const FilterInfo& info, const std::string& counter)
      : Filter(info), counter_idx_(Context::GetDataIndex<Counter>(counter)) {}

  Result Process([[maybe_unused]] const GeoMember& member,
                 Context& context) const override {
    auto counter = context.GetData<int>(counter_idx_, 0);
    context.SetData<int>(counter_idx_, counter + 1);
    return Result::kDisallow;
  }

  static int GetCounter(const Context& context, const std::string& counter) {
    return context.GetData<int>(Context::GetDataIndex<Counter>(counter), 0);
  }

 private:
  const size_t counter_idx_;
};

using Factories = std::unordered_map<std::string, std::shared_ptr<Factory>>;

class CreatingFactoryEnvironment : public FactoryEnvironment {
 public:
  CreatingFactoryEnvironment(const Environment& environment,
                             Factories&& factories)
      : FactoryEnvironment(environment), factories_(std::move(factories)) {}

  std::unique_ptr<Filter> CreateFilter(
      const std::string& name,
      const formats::json::Value& params) const override {
    return factories_.at(name)->Create(params, *this);
  }

 private:
  Factories factories_;
};

using CreatingFactory = DummyFactory<AllowAll>;

class NonCreatingFactory : public DummyFactory<AllowAll> {
  using DummyFactory::DummyFactory;

  std::unique_ptr<Filter> Create(const formats::json::Value&,
                                 const FactoryEnvironment&) const override {
    return {};
  }
};

}  // namespace candidates::filters::test

TEST(AnyOf, RepeatAndNull) {
  std::vector<std::unique_ptr<cf::Filter>> filters;
  filters.push_back(
      std::make_unique<cf::test::Counter>(kEmptyInfo, "counter0"));
  filters.push_back(std::make_unique<cf::test::Repeat>(kEmptyInfo));
  filters.push_back(
      std::make_unique<cf::test::Counter>(kEmptyInfo, "counter2"));

  cfi::AnyOf filter(kAnyOfInfo, std::move(filters));
  cf::Context context;
  EXPECT_EQ(filter.Process({}, context), cf::Result::kRepeat);
  EXPECT_EQ(filter.Process({}, context), cf::Result::kRepeat);
  cf::test::Repeat::SetFlag(context, true);
  EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);
  EXPECT_EQ(cf::test::Counter::GetCounter(context, "counter0"), 1);
  EXPECT_EQ(cf::test::Counter::GetCounter(context, "counter2"), 1);
}

TEST(AnyOfFactory, AllNulls) {
  cf::detail::DummyFactoryEnvironment env(CreateEnvironment());
  cfi::AnyOfFactory factory(kEmptyInfo, {"filter1", "filter2", "filter3"});

  EXPECT_EQ(factory.Create({}, env), nullptr);
}

TEST(AnyOfFactory, ChangedFilterInfo) {
  cf::FilterInfo info = {"any_of", {"dep1", "dep2"}, {}, true, {}};
  cf::FilterInfo info1 = {"filter1", {"dep1"}, {}, true, {}};
  cf::FilterInfo info2 = {"filter2", {"dep2"}, {}, true, {}};
  auto fac1 = std::make_shared<cf::test::CreatingFactory>(info1);
  auto fac2 = std::make_shared<cf::test::NonCreatingFactory>(info2);
  cf::test::Factories factories = {{info1.name, std::move(fac1)},
                                   {info2.name, std::move(fac2)}};

  cf::test::CreatingFactoryEnvironment env(CreateEnvironment(),
                                           std::move(factories));

  cfi::AnyOfFactory any_of_factory(info, {info1.name, info2.name});
  auto filter = any_of_factory.Create({}, env);

  EXPECT_EQ(filter->info().dependencies, info1.dependencies);
}

TEST(AnyOfFactory, UnchangedFilterInfo) {
  cf::FilterInfo info = {"any_of", {"dep1", "dep2"}, {}, true, {}};
  cf::FilterInfo info1 = {"filter1", {"dep1"}, {}, true, {}};
  cf::FilterInfo info2 = {"filter2", {"dep2"}, {}, true, {}};
  auto fac1 = std::make_shared<cf::test::CreatingFactory>(info1);
  auto fac2 = std::make_shared<cf::test::CreatingFactory>(info2);
  cf::test::Factories factories = {{info1.name, std::move(fac1)},
                                   {info2.name, std::move(fac2)}};

  cf::test::CreatingFactoryEnvironment env(CreateEnvironment(),
                                           std::move(factories));

  cfi::AnyOfFactory any_of_factory(info, {info1.name, info2.name});
  auto filter = any_of_factory.Create({}, env);

  EXPECT_TRUE(any_of_factory.info().equal(filter->info()));
}
