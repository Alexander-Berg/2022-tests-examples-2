#include <algorithm>
#include <functional>
#include <iterator>
#include <vector>

#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <dispatch/proposition-builders/delivery/route_generator.hpp>
#include <experiments3/united_dispatch_generators_settings.hpp>
#include <utils/test_helpers.hpp>

using namespace united_dispatch::waybill::delivery;
using namespace united_dispatch::models;
using namespace united_dispatch::test_helpers;
using namespace united_dispatch::waybill::delivery::route_generator;

struct TestInput {
  std::vector<std::vector<std::string>> segments_ids;
  size_t max_packs_per_segment_threshold_for_merge_segment_packs;
  double intersected_threshold_for_merge_segment_packs;
  int answer;
};

int TestMergeSegmentPacks(const TestInput& test) {
  SegmentsPackSet segments_packs_set;
  for (const auto& segments_id : test.segments_ids) {
    std::vector<std::shared_ptr<united_dispatch::models::Segment>> segments;
    for (const auto& segment_id : segments_id) {
      auto kwargs = GenerateSegmentKwargs{};
      kwargs.segment_id = segment_id;
      auto segment = GenerateSegment(kwargs);
      segments.push_back(std::move(segment));
    }
    auto route = GetRouteFromSegments(segments, "test-generator", false);
    segments_packs_set.insert(std::move(route));
  }

  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.max_packs_per_segment_threshold_for_merge_segment_packs =
      test.max_packs_per_segment_threshold_for_merge_segment_packs;
  common_settings.intersected_threshold_for_merge_segment_packs =
      test.intersected_threshold_for_merge_segment_packs;
  GeneratorsSettings generators_settings;
  generators_settings.common = common_settings;

  WaybillRefGeneratorPtr waybill_ref_generator{};

  std::vector<Route> merged_packs = MergeSegmentPacks(
      segments_packs_set, generators_settings, waybill_ref_generator);

  return merged_packs.size();
}

UTEST(RouteGenerator, MergeSegmentPacks1) {
  TestInput test = {
      {
          {"1", "2", "3", "4"},
          {"1", "2", "3"},
      },
      1,
      1,
      2,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}

UTEST(RouteGenerator, MergeSegmentPacks2) {
  TestInput test = {
      {
          {"1", "2", "3", "4"},
          {"1", "2", "3"},
      },
      10,
      0,
      2,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}

UTEST(RouteGenerator, MergeSegmentPacks3) {
  TestInput test = {
      {
          {"1", "2", "3", "4"},
          {"1", "2", "3"},
      },
      1,
      0,
      1,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}

UTEST(RouteGenerator, MergeSegmentPacks4) {
  TestInput test = {
      {
          {"1", "2", "3"},
          {"4", "5", "6"},
      },
      1,
      0,
      2,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}

UTEST(RouteGenerator, MergeSegmentPacks5) {
  TestInput test = {
      {
          {"1", "2", "3"},
          {"3", "4", "5"},
      },
      2,
      0,
      2,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}

UTEST(RouteGenerator, MergeSegmentPacks6) {
  TestInput test = {
      {
          {"1", "2", "3"},
          {"2", "3", "4"},
      },
      2,
      0,
      1,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}

UTEST(RouteGenerator, MergeSegmentPacks7) {
  TestInput test = {
      {
          {"1", "2", "3"},
          {"3", "4", "5"},
          {"5", "6", "7"},
      },
      2,
      0,
      3,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}

UTEST(RouteGenerator, MergeSegmentPacks8) {
  TestInput test = {
      {
          {"1", "2", "3"},
          {"3", "4", "5"},
          {"5", "6", "7"},
      },
      1,
      0,
      1,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}

UTEST(RouteGenerator, MergeSegmentPacks9) {
  TestInput test = {
      {
          {"1", "2", "3"},
          {"3", "4", "5"},
          {"5", "6", "7"},
      },
      1,
      0.5,
      3,
  };

  ASSERT_EQ(TestMergeSegmentPacks(test), test.answer);
}
