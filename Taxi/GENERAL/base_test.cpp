#include <userver/utest/utest.hpp>

#include "base.hpp"

namespace {

using Params = models::candidates::Params;
using ParamsOrder = defs::internal::candidates::ParamsOrder;
using RejectedCandidate = defs::internal::candidates::RejectedCandidate;
using RejectedCandidates = std::vector<RejectedCandidate>;

using models::candidates::ExcludeRejectedCandidates;

using RejectedCandidatesIndex =
    united_dispatch::models::RejectedCandidatesIndex;
using Segment = united_dispatch::models::Segment;
using SegmentPoint = handlers::SegmentPoint;

RejectedCandidates Sorted(const RejectedCandidates& rejected_candidates) {
  RejectedCandidates result = rejected_candidates;
  std::sort(result.begin(), result.end(),
            [](const auto& a, const auto& b) { return a.id < b.id; });
  return result;
}

SegmentPoint CreatePoint(std::optional<std::string> external_order_id) {
  SegmentPoint p;
  p.external_order_id = external_order_id;
  return p;
}

Segment CreateSegment(std::string segment_id,
                      std::optional<std::string> corp_client_id,
                      std::vector<SegmentPoint> points) {
  Segment s;
  s.id = segment_id;
  s.corp_client_id = corp_client_id;
  s.points = points;
  return s;
}

}  // namespace

UTEST(MergeParams, CargoRefIds) {
  const struct {
    std::optional<std::vector<std::string>> c1;
    std::optional<std::vector<std::string>> c2;
    std::optional<std::vector<std::string>> expected;
  } cases[] = {
      {std::nullopt, std::nullopt, std::nullopt},
      {{{"foo"}}, {{"bar"}}, {{"bar", "foo"}}},
      {{{"foo"}}, std::nullopt, {{"foo"}}},
      {std::nullopt, {{"bar"}}, {{"bar"}}},
  };

  for (const auto& sample : cases) {
    Params p1;
    Params p2;

    if (sample.c1.has_value()) {
      p1.order.emplace();
      p1.order->cargo_ref_ids = sample.c1;
    }

    if (sample.c2.has_value()) {
      p2.order.emplace();
      p2.order->cargo_ref_ids = sample.c2;
    }

    const auto result = models::candidates::Merge(p1, p2);
    if (sample.expected.has_value()) {
      EXPECT_TRUE(result.order.has_value());
      EXPECT_TRUE(result.order->cargo_ref_ids.has_value());
      EXPECT_EQ(result.order->cargo_ref_ids.value(), sample.expected.value());
    } else {
      EXPECT_FALSE(result.order.has_value());
    }
  }
}

UTEST(MergeParams, OrderId) {
  const std::string kUnchanged = "unchanged";
  const struct {
    std::optional<std::vector<std::string>> c1;
    std::optional<std::vector<std::string>> c2;
    std::string expected_order_id;
  } cases[] = {
      {std::nullopt, std::nullopt, kUnchanged},
      {{{"foo"}}, {{"bar"}}, "ud/bar/foo"},
      {{{"foo"}}, std::nullopt, kUnchanged},
      {std::nullopt, {{"bar"}}, "ud/bar"},
  };

  for (const auto& sample : cases) {
    Params p1;
    p1.order_id = kUnchanged;
    Params p2;

    if (sample.c1.has_value()) {
      p1.order.emplace();
      p1.order->cargo_ref_ids = sample.c1;
    }

    if (sample.c2.has_value()) {
      p2.order.emplace();
      p2.order->cargo_ref_ids = sample.c2;
    }

    const auto result = models::candidates::Merge(p1, p2);

    EXPECT_EQ(result.order_id, sample.expected_order_id);
  }
}

UTEST(MergeParams, Requirements) {
  const struct {
    std::optional<std::string> req1;
    std::optional<std::string> req2;
    std::optional<std::string> expected;
  } cases[] = {
      {std::nullopt, std::nullopt, std::nullopt},
      {{R"({"foo": true})"},
       {R"({"bar": true})"},
       {R"({"foo": true, "bar": true})"}},
      {std::nullopt, {R"({"bar": true})"}, {R"({"bar": true})"}},
      {{R"({"foo": true})"}, std::nullopt, {R"({"foo": true})"}},
      {{R"({"foo": true})"}, {R"({"foo": false})"}, {R"({"foo": true})"}},
  };

  for (const auto& sample : cases) {
    Params p1;
    Params p2;

    if (sample.req1.has_value()) {
      p1.requirements.emplace();
      p1.requirements->extra = formats::json::FromString(sample.req1.value());
    }

    if (sample.req2.has_value()) {
      p2.requirements.emplace();
      p2.requirements->extra = formats::json::FromString(sample.req2.value());
    }

    const auto result = models::candidates::Merge(p1, p2);

    if (sample.expected.has_value()) {
      EXPECT_TRUE(result.requirements.has_value());
      EXPECT_EQ(result.requirements->extra,
                formats::json::FromString(sample.expected.value()));
    } else {
      EXPECT_FALSE(result.requirements.has_value());
    }
  }
}

UTEST(MergeParams, VirtualTariffs) {
  const struct {
    std::string c1;
    std::string c2;
    std::string expected;
  } cases[] = {{R"({})", R"({})", R"({})"},
               {R"({"virtual_tariffs":
         [
           {"class": "cargo",
            "special_requirements": [
                {"id": "cargo_pickup_points"}
             ]
           }
         ]
        })",
                R"({})",
                R"({"virtual_tariffs":
         [
           {"class": "cargo",
            "special_requirements": [
                {"id": "cargo_pickup_points"}
             ]
           }
         ]
        })"},
               {R"({"virtual_tariffs":
         [
           {"class": "cargo",
            "special_requirements": [
                {"id": "cargo_pickup_points"}
             ]
           }
         ]
        })",
                R"({"virtual_tariffs":
         [
           {"class": "cargo",
            "special_requirements": [
                {"id": "cargo_pickup_points"},
                {"id": "test2"}
             ]
           }
         ]
        })",
                R"({"virtual_tariffs":
         [
           {"class": "cargo",
            "special_requirements": [
                {"id": "cargo_pickup_points"},
                {"id": "test2"}
             ]
           }
         ]
        })"}};

  for (const auto& sample : cases) {
    Params p1;
    p1.order =
        defs::internal::candidates::Parse(formats::json::FromString(sample.c1),
                                          formats::parse::To<ParamsOrder>());
    Params p2;
    p2.order =
        defs::internal::candidates::Parse(formats::json::FromString(sample.c2),
                                          formats::parse::To<ParamsOrder>());

    const auto result = models::candidates::Merge(p1, p2);
    EXPECT_TRUE(result.order.has_value());

    const auto& json = defs::internal::candidates::Serialize(
        result.order.value(),
        ::formats::serialize::To<::formats::json::Value>());
    EXPECT_EQ(json, formats::json::FromString(sample.expected));
  }
}

UTEST(MergeParams, RejectedCandidates) {
  Params p1;
  Params p2;

  p1.order.emplace();
  p1.order->request.emplace();
  p1.order->request->rejected_candidates.emplace();
  p1.order->request->rejected_candidates->push_back({"id1", 1});

  auto result = models::candidates::Merge(p1, p2);
  EXPECT_EQ(result.order->request->rejected_candidates,
            p1.order->request->rejected_candidates);

  result = models::candidates::Merge(p2, p1);
  EXPECT_EQ(result.order->request->rejected_candidates,
            p1.order->request->rejected_candidates);

  p2.order.emplace();
  p2.order->request.emplace();
  p2.order->request->rejected_candidates.emplace();
  p2.order->request->rejected_candidates->push_back({"id2", 2});

  result = models::candidates::Merge(p1, p2);
  EXPECT_EQ(Sorted(result.order->request->rejected_candidates.value()),
            Sorted(RejectedCandidates{{"id2", 2}, {"id1", 1}}));

  result = models::candidates::Merge(p2, p1);
  EXPECT_EQ(Sorted(result.order->request->rejected_candidates.value()),
            Sorted(RejectedCandidates{{"id1", 1}, {"id2", 2}}));

  p2.order->request->rejected_candidates->push_back({"id1", 3});

  result = models::candidates::Merge(p1, p2);
  EXPECT_EQ(Sorted(result.order->request->rejected_candidates.value()),
            Sorted(RejectedCandidates{{"id2", 2}, {"id1", 3}}));
}

UTEST(MakeParams, MakeRejectedCandidate) {
  RejectedCandidatesIndex rejected_candidates = {
      {"s1", {{"id0", {1}}}},     {"cc1_o1", {{"id1", {1}}}},
      {"s2", {{"id3", {1}}}},     {"cc2_o1", {{"id0", {1}}}},
      {"cc2_o2", {{"id0", {1}}}}, {"s3", {{"id4", {1}}}}};

  united_dispatch::waybill::Environment env;
  env.planner_type = united_dispatch::models::PlannerType::kTestsuiteCandidates;
  env.rejected_candidates =
      std::make_shared<RejectedCandidatesIndex>(rejected_candidates);

  auto p0 = CreatePoint(std::nullopt);
  auto p1 = CreatePoint("o1");
  auto p2 = CreatePoint("o2");

  Segment seg1 = CreateSegment("s1", "cc1", {p0, p1, p2});
  Segment seg2 = CreateSegment("s2", "cc2", {p0, p0});
  Segment seg3 = CreateSegment("s3", std::nullopt, {p0, p1, p2});

  auto params = models::candidates::MakeParams(seg1, env);
  EXPECT_EQ(Sorted(params.order->request->rejected_candidates.value()),
            Sorted(RejectedCandidates{{"id1", 1}}));

  params = models::candidates::MakeParams(seg2, env);
  EXPECT_EQ(Sorted(params.order->request->rejected_candidates.value()),
            Sorted(RejectedCandidates{{"id3", 1}}));

  params = models::candidates::MakeParams(seg3, env);
  EXPECT_EQ(Sorted(params.order->request->rejected_candidates.value()),
            Sorted(RejectedCandidates{{"id4", 1}}));
}

UTEST(ExcludeRejectedCandidates, RejectCandidates) {
  models::candidates::Params params;
  params.order = defs::internal::candidates::ParamsOrder();
  params.order.value().request =
      ::defs::internal::candidates::ParamsOrderRequest();

  std::vector<RejectedCandidate> rejected_candidates = {{"dbid1_uuid1", 0},
                                                        {"dbid2_uuid2", 1},
                                                        {"dbid3_uuid3", 2},
                                                        {"dbid4_uuid4", 3}};
  params.order.value().request.value().rejected_candidates =
      rejected_candidates;

  ExcludeRejectedCandidates(params, 0);
  EXPECT_EQ(params.excluded_contractor_ids.value().size(), 3);
  params.excluded_contractor_ids.value().clear();

  ExcludeRejectedCandidates(params, 1);
  EXPECT_EQ(params.excluded_contractor_ids.value().size(), 2);
  params.excluded_contractor_ids.value().clear();

  ExcludeRejectedCandidates(params, 2);
  EXPECT_EQ(params.excluded_contractor_ids.value().size(), 1);
  params.excluded_contractor_ids.value().clear();

  ExcludeRejectedCandidates(params, 3);
  EXPECT_EQ(params.excluded_contractor_ids.value().size(), 0);
}
