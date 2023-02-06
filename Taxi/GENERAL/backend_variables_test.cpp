#include <gmock/gmock-matchers.h>
#include <gmock/gmock-more-matchers.h>
#include <pricing-extended/utils/read_order_proc.hpp>
#include <userver/engine/mutex.hpp>
#include <userver/utest/utest.hpp>
#include <utils/backend_variables/processors/processors_graph.hpp>
#include <utils/backend_variables/sources/sources_graph.hpp>

#include <utils/backend_variables/sources/all_sources.hpp>
#include <utils/backend_variables/sources/alt_offer_discount.hpp>
#include <utils/backend_variables/sources/cashback_rate_source.hpp>
#include <utils/backend_variables/sources/category_information.hpp>
#include <utils/backend_variables/sources/combo_source.hpp>
#include <utils/backend_variables/sources/corp_tariff_source.hpp>
#include <utils/backend_variables/sources/coupon_source.hpp>
#include <utils/backend_variables/sources/experiments3_source.hpp>
#include <utils/backend_variables/sources/ride_discount_source.hpp>
#include <utils/backend_variables/sources/route_source.hpp>
#include <utils/backend_variables/sources/sources_graph.hpp>
#include <utils/backend_variables/sources/surge_source.hpp>
#include <utils/backend_variables/sources/tariff_information.hpp>
#include <utils/backend_variables/sources/umlaas_source.hpp>
#include <utils/backend_variables/sources/user_tags_source.hpp>

enum class CustomSourceId { kA, kB, kC, kD, kE };

enum class CustomProcessorId { kA, kB, kC, kD, kE };

std::string ToString(CustomSourceId sid) {
  switch (sid) {
    case CustomSourceId::kA:
      return "A";
    case CustomSourceId::kB:
      return "B";
    case CustomSourceId::kC:
      return "C";
    case CustomSourceId::kD:
      return "D";
    case CustomSourceId::kE:
      return "E";
  }
}

std::string ToString(CustomProcessorId pid) {
  switch (pid) {
    case CustomProcessorId::kA:
      return "A";
    case CustomProcessorId::kB:
      return "B";
    case CustomProcessorId::kC:
      return "C";
    case CustomProcessorId::kD:
      return "D";
    case CustomProcessorId::kE:
      return "E";
  }
}

logging::LogHelper& operator<<(logging::LogHelper& lh, CustomSourceId sid) {
  lh << ToString(sid);
  return lh;
}

logging::LogHelper& operator<<(logging::LogHelper& lh, CustomProcessorId pid) {
  lh << ToString(pid);
  return lh;
}

template <typename IdT>
struct CallRecorder {
  engine::Mutex mutex;
  std::vector<IdT> load_order;

  void Record(IdT sid) {
    std::lock_guard lock{mutex};
    load_order.push_back(sid);
  }

  size_t TotalLoads() {
    std::lock_guard lock{mutex};
    return load_order.size();
  }

  std::vector<IdT> GetOrder() const { return load_order; }

  bool CheckOrdering(const std::vector<IdT>& befores, IdT after) {
    return std::all_of(befores.begin(), befores.end(),
                       [after, this](const auto before) {
                         return this->CheckOrdering(before, after);
                       });
  }

  bool CheckOrdering(IdT before, IdT after) {
    std::lock_guard lock{mutex};
    const auto bit = std::find(load_order.begin(), load_order.end(), before);
    const auto ait = std::find(load_order.begin(), load_order.end(), after);
    if (bit == load_order.end() || ait == load_order.end()) return false;
    return bit < ait;
  }
};

using SourceLoadRecorder = CallRecorder<CustomSourceId>;
using ProcessorCallRecorder = CallRecorder<CustomProcessorId>;
using DataContext =
    utils::backend_variables::AbstractFetchDataContext<CustomSourceId>;

template <CustomSourceId source_id_, typename... RequiredSources>
struct DummySource
    : public utils::backend_variables::SourceBase<CustomSourceId, int,
                                                  source_id_> {
  std::tuple<std::shared_ptr<RequiredSources>...> sources_links_;
  SourceLoadRecorder* source_recorder = nullptr;

  DummySource()
      : sources_links_(this->template GetSource<RequiredSources>()...) {}

  explicit DummySource(SourceLoadRecorder& rec)
      : sources_links_(this->template GetSource<RequiredSources>()...),
        source_recorder(&rec) {}

  int Get(DataContext&,
          utils::backend_variables::SourceDependencies) const override {
    if (source_recorder != nullptr) {
      source_recorder->Record(source_id_);
    }
    return 42;
  }
};

template <typename... Sources>
struct DummyProcessor : public utils::backend_variables::AbstractProcessorBase<
                            CustomSourceId, CustomProcessorId> {
  CustomProcessorId self_id;
  std::vector<CustomProcessorId> dependents_processors;
  std::vector<std::shared_ptr<
      utils::backend_variables::AbstractSourceBase<CustomSourceId>>>
      required_sources;
  utils::backend_variables::UpdateContextResult update_result =
      utils::backend_variables::UpdateContextResult::kNotUsed;
  ProcessorCallRecorder* recorder = nullptr;

  DummyProcessor(CustomProcessorId self_id,
                 const std::vector<CustomProcessorId>& dependents_processors,
                 utils::backend_variables::UpdateContextResult update_result =
                     utils::backend_variables::UpdateContextResult::kApplied)
      : self_id(self_id),
        dependents_processors(dependents_processors),
        required_sources{GetSource<Sources>()...},
        update_result(update_result) {}

  DummyProcessor(CustomProcessorId self_id,
                 const std::vector<CustomProcessorId>& dependents_processors,
                 ProcessorCallRecorder& rec,
                 utils::backend_variables::UpdateContextResult update_result =
                     utils::backend_variables::UpdateContextResult::kApplied)
      : self_id(self_id),
        dependents_processors(dependents_processors),
        update_result(update_result),
        recorder(&rec) {}

  utils::backend_variables::UpdateContextResult UpdateContext(
      const DataContext&, const utils::backend_variables::UpdateRequestData&,
      utils::backend_variables::UpdateBvProcessorContext&,
      const utils::backend_variables::ProcessorDeps&) const override {
    if (recorder) {
      recorder->Record(self_id);
    }
    return update_result;
  }

  utils::backend_variables::UpdateContextResult UpdateContext(
      const DataContext&, const handlers::PrepareRequest&,
      utils::backend_variables::CreateBvProcessorContext&,
      const utils::backend_variables::ProcessorDeps&) const override {
    if (recorder) {
      recorder->Record(self_id);
    }
    return update_result;
  }

  std::vector<CustomProcessorId> GetDependentsProcessors() const override {
    return dependents_processors;
  }

  std::vector<utils::backend_variables::BackendVariablesField>
  GetAffectedBVFields() const override {
    return {};
  }

  CustomProcessorId GetId() const override { return self_id; }
};

template <typename... Source>
std::unordered_map<CustomSourceId,
                   std::shared_ptr<utils::backend_variables::AbstractSourceBase<
                       CustomSourceId>>>
MakeSourceMap() {
  return {{std::make_pair(Source::source_id, std::make_shared<Source>())...}};
}

template <typename... Source>
std::unordered_map<CustomSourceId,
                   std::shared_ptr<utils::backend_variables::AbstractSourceBase<
                       CustomSourceId>>>
MakeSourceMap(SourceLoadRecorder& rec) {
  return {
      {std::make_pair(Source::source_id, std::make_shared<Source>(rec))...}};
}

using AbstractCustomProcessors =
    utils::backend_variables::AbstractProcessorBase<CustomSourceId,
                                                    CustomProcessorId>;
using AbstractCustomProcessorsPtr = std::unique_ptr<AbstractCustomProcessors>;

template <typename... Processors>
std::unordered_map<CustomProcessorId, AbstractCustomProcessorsPtr>
MakeProcessorsMap(Processors... processors) {
  AbstractCustomProcessorsPtr procs_array[] = {
      std::make_unique<Processors>(std::move(processors))...};
  std::unordered_map<CustomProcessorId, AbstractCustomProcessorsPtr> result{};
  for (auto&& proc : procs_array) {
    const auto pid = proc->GetId();
    result.emplace(pid, std::move(proc));
  }
  return result;
}

TEST(BackendVariablesUtils, SourceDependenciesBuildTest) {
  using RequiredSourcesMap =
      std::unordered_map<CustomSourceId, std::vector<CustomSourceId>>;
  {
    using a_noreq = DummySource<CustomSourceId::kA>;
    RequiredSourcesMap expected_map{{CustomSourceId::kA, {}}};
    ASSERT_EQ(utils::backend_variables::FetchSourceDependencies(
                  MakeSourceMap<a_noreq>()),
              expected_map);
  }

  {
    using a_no_req = DummySource<CustomSourceId::kA>;
    using b_req_a = DummySource<CustomSourceId::kB, a_no_req>;
    using c_req_a = DummySource<CustomSourceId::kC, a_no_req>;
    RequiredSourcesMap expected_map{
        {CustomSourceId::kA, {CustomSourceId::kB, CustomSourceId::kC}},
        {CustomSourceId::kB, {}},
        {CustomSourceId::kC, {}}};
    auto source_map = MakeSourceMap<a_no_req, b_req_a, c_req_a>();
    auto result = utils::backend_variables::FetchSourceDependencies(source_map);
    for (auto& [source, source_deps] : result) {
      std::sort(source_deps.begin(), source_deps.end());
    }
    ASSERT_THAT(result, ::testing::ContainerEq(expected_map));
  }
}

TEST(BackendVariablesUtils, ProcessorRequiredSourceTest) {
  {
    using source_a = DummySource<CustomSourceId::kA>;
    DummyProcessor<source_a> proc_a{CustomProcessorId::kA, {}};
    std::unordered_set<CustomSourceId> expected_sources{CustomSourceId::kA};
    auto source_map = MakeSourceMap<source_a>();
    auto proc_map = MakeProcessorsMap(proc_a);
    ASSERT_THAT(
        FetchRequiredSources(CustomProcessorId::kA, source_map, proc_map),
        ::testing::ContainerEq(expected_sources));
  }

  {
    using source_d = DummySource<CustomSourceId::kD>;
    using source_c = DummySource<CustomSourceId::kC, source_d>;
    using source_b = DummySource<CustomSourceId::kB, source_d>;
    using source_a = DummySource<CustomSourceId::kA, source_b, source_c>;
    DummyProcessor<source_a> proc_a{CustomProcessorId::kA, {}};

    std::unordered_set<CustomSourceId> expected_sources{
        CustomSourceId::kA, CustomSourceId::kB, CustomSourceId::kC,
        CustomSourceId::kD};
    auto source_map = MakeSourceMap<source_a, source_b, source_c, source_d>();
    auto proc_map = MakeProcessorsMap(proc_a);
    ASSERT_THAT(
        FetchRequiredSources(CustomProcessorId::kA, source_map, proc_map),
        ::testing::ContainerEq(expected_sources));
  }

  {
    using source_d = DummySource<CustomSourceId::kD>;
    using source_c = DummySource<CustomSourceId::kC>;
    using source_a = DummySource<CustomSourceId::kA, source_d>;
    using source_b = DummySource<CustomSourceId::kB, source_a, source_c>;

    DummyProcessor<source_a> proc_a{CustomProcessorId::kA,
                                    {CustomProcessorId::kB}};
    DummyProcessor<source_b> proc_b{CustomProcessorId::kB, {}};

    std::unordered_set<CustomSourceId> expected_sources{
        CustomSourceId::kA, CustomSourceId::kB, CustomSourceId::kC,
        CustomSourceId::kD};
    auto source_map = MakeSourceMap<source_a, source_b, source_c, source_d>();
    auto proc_map = MakeProcessorsMap(proc_a, proc_b);
    ASSERT_THAT(
        FetchRequiredSources(CustomProcessorId::kA, source_map, proc_map),
        ::testing::ContainerEq(expected_sources));
  }
}

UTEST(BackendVariablesUtils, LoadSourcesTest) {
  {
    SourceLoadRecorder rec;
    using source_c = DummySource<CustomSourceId::kC>;
    using source_d = DummySource<CustomSourceId::kD>;
    using source_a = DummySource<CustomSourceId::kA, source_d>;
    using source_b = DummySource<CustomSourceId::kB, source_a, source_c>;

    auto source_map =
        MakeSourceMap<source_a, source_b, source_c, source_d>(rec);
    DataContext ctx{{}};
    LoadSources(source_map,
                {CustomSourceId::kA, CustomSourceId::kB, CustomSourceId::kC,
                 CustomSourceId::kD},
                ctx, {});
    ASSERT_EQ(rec.TotalLoads(), 4);
    ASSERT_TRUE(rec.CheckOrdering(CustomSourceId::kD, CustomSourceId::kA));
    ASSERT_TRUE(rec.CheckOrdering(
        {CustomSourceId::kA, CustomSourceId::kC, CustomSourceId::kD},
        CustomSourceId::kB));
  }

  {
    SourceLoadRecorder rec;
    using source_d = DummySource<CustomSourceId::kD>;
    using source_b = DummySource<CustomSourceId::kB, source_d>;
    using source_c = DummySource<CustomSourceId::kC, source_d>;
    using source_a = DummySource<CustomSourceId::kA, source_b, source_c>;
    auto source_map =
        MakeSourceMap<source_a, source_b, source_c, source_d>(rec);
    DataContext ctx{{}};
    LoadSources(source_map,
                {CustomSourceId::kA, CustomSourceId::kB, CustomSourceId::kC,
                 CustomSourceId::kD},
                ctx, {});
    ASSERT_EQ(rec.TotalLoads(), 4);
    ASSERT_TRUE(rec.CheckOrdering(
        {CustomSourceId::kD, CustomSourceId::kB, CustomSourceId::kC},
        CustomSourceId::kA));
    ASSERT_TRUE(rec.CheckOrdering(CustomSourceId::kD, CustomSourceId::kB));
    ASSERT_TRUE(rec.CheckOrdering(CustomSourceId::kD, CustomSourceId::kC));
  }

  {
    SourceLoadRecorder rec;
    using source_d = DummySource<CustomSourceId::kD>;
    using source_c = DummySource<CustomSourceId::kC, source_d>;
    using source_b = DummySource<CustomSourceId::kB, source_c>;
    using source_a = DummySource<CustomSourceId::kA, source_b>;
    auto source_map =
        MakeSourceMap<source_a, source_b, source_c, source_d>(rec);

    DataContext ctx{{}};
    LoadSources(source_map,
                {CustomSourceId::kA, CustomSourceId::kB, CustomSourceId::kC,
                 CustomSourceId::kD},
                ctx, {});
    ASSERT_EQ(rec.TotalLoads(), 4);
    ASSERT_TRUE(rec.CheckOrdering(CustomSourceId::kD, CustomSourceId::kC));
    ASSERT_TRUE(rec.CheckOrdering(CustomSourceId::kC, CustomSourceId::kB));
    ASSERT_TRUE(rec.CheckOrdering(CustomSourceId::kB, CustomSourceId::kA));
  }
}

UTEST(BackendVariablesUtils, ProcessorsUpdateTest) {
  utils::backend_variables::ProcessorDeps pdeps{};
  {
    DataContext ctx{{}};
    utils::backend_variables::UpdateRequestData rd{};
    utils::backend_variables::UpdateBvProcessorContext pctx{};
    ProcessorCallRecorder recorder;
    DummyProcessor a{CustomProcessorId::kA,
                     {CustomProcessorId::kB},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    DummyProcessor b{CustomProcessorId::kB,
                     {CustomProcessorId::kC, CustomProcessorId::kD},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    DummyProcessor c{CustomProcessorId::kC,
                     {CustomProcessorId::kE},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    DummyProcessor d{CustomProcessorId::kD,
                     {},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    DummyProcessor e{CustomProcessorId::kE,
                     {},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    utils::backend_variables::CascadeUpdateContext(
        CustomProcessorId::kA, ctx, rd, pctx, MakeProcessorsMap(a, b, c, d, e),
        pdeps);
    ASSERT_THAT(
        recorder.GetOrder(),
        testing::ElementsAre(CustomProcessorId::kA, CustomProcessorId::kB,
                             CustomProcessorId::kC, CustomProcessorId::kE,
                             CustomProcessorId::kD));
  }

  {
    DataContext ctx{{}};
    utils::backend_variables::UpdateRequestData rd{};
    utils::backend_variables::UpdateBvProcessorContext pctx{};
    ProcessorCallRecorder recorder;
    DummyProcessor a{CustomProcessorId::kA,
                     {CustomProcessorId::kB},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    DummyProcessor b{CustomProcessorId::kB,
                     {CustomProcessorId::kC, CustomProcessorId::kD},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    DummyProcessor c{CustomProcessorId::kC,
                     {CustomProcessorId::kE},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kNotUsed};
    DummyProcessor d{CustomProcessorId::kD,
                     {},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    DummyProcessor e{CustomProcessorId::kE,
                     {},
                     recorder,
                     utils::backend_variables::UpdateContextResult::kApplied};
    utils::backend_variables::CascadeUpdateContext(
        CustomProcessorId::kA, ctx, rd, pctx, MakeProcessorsMap(a, b, c, d, e),
        pdeps);
    ASSERT_THAT(
        recorder.GetOrder(),
        testing::ElementsAre(CustomProcessorId::kA, CustomProcessorId::kB,
                             CustomProcessorId::kC, CustomProcessorId::kD));
  }
}
