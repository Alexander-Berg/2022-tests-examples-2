#include "candidates.hpp"

#include <userver/logging/log.hpp>
#include <userver/utils/algo.hpp>

#include <dispatch/proposition-builders/delivery.hpp>

#include <handlers/dependencies.hpp>

#include <components/candidates.hpp>
#include <models/united_dispatch/waybill_ref.hpp>
#include <utils/waybill_create.hpp>

namespace united_dispatch::waybill {

namespace {

using namespace ::models::candidates;

enum class TestType { kUnknown, kGreedy, kBatch, kLiveBatch };

class DummyWaybillFilter : public ::models::candidates::waybill::Filter {
 public:
  Result Process(const ::models::candidates::waybill::Candidate&,
                 const uint32_t) const override {
    return Result::kAllow;
  }
};

const std::string kScoringIntent = "ud-candidates-testsuite";

TestType GetTestType(const Segment& segment) {
  if (segment.corp_client_id != "candidates-testsuite" ||
      !segment.custom_context)
    return TestType::kUnknown;

  const auto& custom_context = *segment.custom_context;
  const auto& type_field = custom_context["candidates-testsuite"]["type"];
  if (type_field.IsMissing()) return TestType::kUnknown;

  const auto& type = type_field.As<std::string>();
  if (type == "greedy") return TestType::kGreedy;
  if (type == "batch") return TestType::kBatch;
  if (type == "live_batch") return TestType::kLiveBatch;
  return TestType::kUnknown;
}

std::vector<SegmentPtr> GetSegments(const Input& input, const TestType type) {
  std::vector<SegmentPtr> segments;
  for (const auto& input_segment : input.segments) {
    const auto& segment = input_segment.data;
    if (GetTestType(*segment) != type) continue;

    segments.push_back(segment);
  }
  return segments;
}

template <typename CandidatesPtr>
struct SegmentWithCandidates {
  SegmentPtr segment;
  CandidatesPtr candidates;
};

template <typename CandidatesPtr>
std::vector<SegmentWithCandidates<CandidatesPtr>> ZipSegments(
    const std::vector<SegmentPtr>& segments,
    const std::vector<CandidatesPtr>& candidates) {
  std::vector<SegmentWithCandidates<CandidatesPtr>> segments_with_candidates;
  segments_with_candidates.reserve(segments.size());
  for (size_t i = 0; i < segments.size(); ++i) {
    const auto& segment = segments.at(i);
    const auto& segment_candidates = candidates.at(i);

    if (!segment_candidates) {
      LOG_ERROR() << "failed to get candidates for " << segment->id;
      continue;
    }
    if (segment_candidates->candidates.empty()) {
      LOG_INFO() << "no candidates for " << segment->id;
      continue;
    }

    segments_with_candidates.push_back({segment, segment_candidates});
  }

  return segments_with_candidates;
}

std::vector<SegmentWithCandidates<::models::candidates::CandidatesPtr>>
GetCandidates(const std::vector<SegmentPtr>& segments,
              const ::views::candidates::Candidates& candidates,
              const Environment& environment, bool need_satisfy = false) {
  std::vector<Params> params;
  params.reserve(segments.size());
  for (const auto& segment : segments) {
    auto segment_params = MakeParams(*segment, environment);
    ExcludeRejectedCandidates(segment_params);

    params.push_back(std::move(segment_params));
  }

  auto segments_candidates = candidates.GetCandidates(params, need_satisfy);
  return ZipSegments(segments, segments_candidates);
}

std::vector<SegmentWithCandidates<ScoredCandidatesPtr>> ScoreCandidates(
    const std::vector<SegmentWithCandidates<CandidatesPtr>>&
        segments_with_candidates,
    const ::views::candidates::Candidates& candidates,
    const Environment& environment) {
  std::vector<ScoringParams> scoring_params;
  scoring_params.reserve(segments_with_candidates.size());
  std::vector<SegmentPtr> segments;
  for (const auto& [segment, segment_candidates] : segments_with_candidates) {
    ScoringParams params;
    params.params = MakeParams(*segment, environment);
    if (segment_candidates) {
      params.candidates = segment_candidates->candidates;
    }
    scoring_params.push_back(std::move(params));
    segments.push_back(segment);
  }
  auto scored_candidates = candidates.ScoreCandidates(scoring_params);
  return ZipSegments(segments, scored_candidates);
}

// Fetch candidates for each segment and propose best
void DoGreedyPropositions(
    Output& output, const Input& input,
    const ::views::candidates::Candidates& candidates,
    const Environment& environment,
    const models::WaybillRefGeneratorPtr& waybill_ref_generator) {
  auto segments = GetSegments(input, TestType::kGreedy);
  if (segments.empty()) return;

  const auto& segments_with_candidates =
      GetCandidates(segments, candidates, environment);

  const auto& scored_segments_with_candidates =
      ScoreCandidates(segments_with_candidates, candidates, environment);

  for (const auto& segment_with_candidates : scored_segments_with_candidates) {
    auto waybill = CreateWaybill(segment_with_candidates.segment);
    waybill.SetCandidate(
        *segment_with_candidates.candidates->candidates.front());
    output.AddProposition(std::move(waybill), waybill_ref_generator);
  }
}

// Fetch candidates for each segment, assume each segment is a batch, score
// found candidates and propose best
void DoBatchPropositions(
    Output& output, const Input& input,
    const ::views::candidates::Candidates& candidates,
    const Environment& environment,
    const models::WaybillRefGeneratorPtr& waybill_ref_generator) {
  auto segments = GetSegments(input, TestType::kBatch);
  if (segments.empty()) return;

  const auto& segments_with_candidates =
      GetCandidates(segments, candidates, environment, true);

  if (segments_with_candidates.empty()) return;

  const auto& segments_with_scored_candidates =
      ScoreCandidates(segments_with_candidates, candidates, environment);

  if (segments_with_scored_candidates.empty()) return;

  for (const auto& segment_with_scored_candidates :
       segments_with_scored_candidates) {
    auto waybill = CreateWaybill(segment_with_scored_candidates.segment);
    waybill.SetCandidate(
        *segment_with_scored_candidates.candidates->candidates.front());
    output.AddProposition(std::move(waybill), waybill_ref_generator);
  }
}

// Fetch on order candidates for each segment, assume each segment is for a live
// batch, propose best
void DoLiveBatchPropositions(
    Output& output, const Input& input,
    const ::views::candidates::Candidates& candidates,
    const Environment& environment,
    const models::WaybillRefGeneratorPtr& waybill_ref_generator) {
  auto segments = GetSegments(input, TestType::kLiveBatch);
  if (segments.empty()) return;

  std::vector<OnOrderParams> on_order_params;
  on_order_params.reserve(segments.size());
  for (const auto& segment : segments) {
    OnOrderParams params;
    params.params = MakeParams(*segment, environment);
    params.search_settings.limit = 10;
    params.search_settings.max_distance = 10000;
    params.whitelisted_filters = {candidates_filters::kMetaStatusSearchable};
    params.filter = std::make_unique<DummyWaybillFilter>();
    on_order_params.push_back(std::move(params));
  }

  const auto& on_order_candidates =
      candidates.GetCandidatesOnOrder(on_order_params);
  auto segments_with_candidates = ZipSegments(segments, on_order_candidates);

  const auto& scored_segments_with_candidates =
      ScoreCandidates(segments_with_candidates, candidates, environment);

  if (scored_segments_with_candidates.empty()) return;

  for (size_t segment_idx = 0;
       segment_idx < scored_segments_with_candidates.size(); ++segment_idx) {
    const auto& [segment, scored_candidates] =
        scored_segments_with_candidates[segment_idx];
    const auto& segment_candidates =
        segments_with_candidates[segment_idx].candidates;
    std::unordered_map<std::string_view, const std::vector<WaybillProposalPtr>*>
        candidate_waybills;
    for (size_t candidate_idx = 0;
         candidate_idx < segment_candidates->candidates.size();
         ++candidate_idx) {
      const auto& candidate = segment_candidates->candidates[candidate_idx];
      const auto& waybills = segment_candidates->waybills[candidate_idx];
      candidate_waybills.emplace(candidate->id, &waybills);
    }
    const auto& candidate = scored_candidates->candidates.front();
    auto* waybills_ptr =
        ::utils::FindOrDefault(candidate_waybills, candidate->id);
    if (!waybills_ptr || waybills_ptr->empty()) {
      LOG_INFO() << fmt::format("No waybills for candidate {}", candidate->id);
      continue;
    }
    const auto& waybills = *waybills_ptr;
    if (waybills.size() > 1) {
      LOG_INFO() << fmt::format(
          "Live batch only for single waybill on candidate. candidate {} has "
          "{} waybills",
          candidate->id, waybills.size());
      continue;
    }

    auto waybill = CreateWaybill(segment);
    waybill.SetCandidate(*candidate);
    output.AddProposition(std::move(waybill), waybill_ref_generator);
  }
}

// Fetch new candidates for the input idle waybills and reassign best
void DoRepeatWaybillSearch(Output& output, const Input& input,
                           const ::views::candidates::Candidates& candidates,
                           const Environment& environment) {
  if (input.waybills.empty()) return;

  std::unordered_map<std::string, WaybillProposalPtr> waybills_by_segment_id;
  std::vector<SegmentPtr> segments;
  for (const auto& waybill : input.waybills) {
    if (!waybill->IsLookupRequested()) {
      // process only idle segments yet
      continue;
    }
    if (waybill->segments.empty()) continue;
    const auto& segment = waybill->segments.front();
    segments.push_back(segment);
    waybills_by_segment_id[segment->id] = waybill;
  }
  if (segments.empty()) return;

  const auto& segments_with_candidates =
      GetCandidates(segments, candidates, environment);

  const auto& scored_segments_with_candidates =
      ScoreCandidates(segments_with_candidates, candidates, environment);

  for (const auto& segment_with_candidates : scored_segments_with_candidates) {
    const auto waybill_it =
        waybills_by_segment_id.find(segment_with_candidates.segment->id);
    if (waybill_it == waybills_by_segment_id.end()) continue;
    const auto& waybill = waybill_it->second;
    output.AddWaybillCandidate(
        *waybill, segment_with_candidates.candidates->candidates.front());
  }
}

}  // namespace

bool TestsuiteCandidatesPlanner::FilterWaybill(
    [[maybe_unused]] const WaybillProposal& waybill,
    [[maybe_unused]] const handlers::Dependencies& dependencies) const {
  return waybill.segments.size() == 1;
}

Output TestsuiteCandidatesPlanner::Run(
    const Input& input, const Environment& environment,
    const handlers::Dependencies& dependencies) const {
  const auto& candidates = dependencies.extra.candidates.Get(
      kScoringIntent, environment, dependencies);

  auto waybill_ref_generator = std::make_shared<models::WaybillRefGenerator>(
      GetPlannerType(), environment, dependencies.pg_united_dispatch);

  Output output;
  DoGreedyPropositions(output, input, *candidates, environment,
                       waybill_ref_generator);
  DoBatchPropositions(output, input, *candidates, environment,
                      waybill_ref_generator);
  DoLiveBatchPropositions(output, input, *candidates, environment,
                          waybill_ref_generator);
  DoRepeatWaybillSearch(output, input, *candidates, environment);

  return output;
}

}  // namespace united_dispatch::waybill
