#include <gtest/gtest.h>
#include <memory>
#include <userver/utest/utest.hpp>

#include "proposition-applier.hpp"

#include <models/united_dispatch/segment.hpp>

UTEST(PropositionApplierTest, BuildWaybillProposalP2P) {
  auto segment = std::make_shared<united_dispatch::models::Segment>();
  segment->taxi_classes = {"courier", "express"};
  segment->taxi_requirements =
      formats::json::FromString(R"({"taxi_req_1": true})");
  handlers::SpecialRequirements sr{};
  handlers::VirtualTariff vt1{"courier",
                              {handlers::SpecialRequirement{"req1"}}};
  sr.virtual_tariffs.push_back(vt1);
  segment->special_requirements = sr;
  united_dispatch::waybill::WaybillProposal ud_waybill{};
  ud_waybill.segments = {segment};
  auto cargo_waybill =
      united_dispatch::waybill::BuildWaybillProposal(ud_waybill);

  auto expected_taxi_order_requirements_extra = formats::json::FromString(R"(
        {"taxi_classes": ["courier", "express"], "taxi_req_1": true}
    )");
  EXPECT_EQ(cargo_waybill.taxi_order_requirements.extra,
            expected_taxi_order_requirements_extra);
  auto expected_special_requirements_json = formats::json::FromString(R"(
        {
            "virtual_tariffs":[{"class":"courier","special_requirements":[{"id":"req1"}]}]
        }
    )");
  auto result_special_requirements_json = clients::cargo_dispatch::Serialize(
      cargo_waybill.special_requirements,
      formats::serialize::To<formats::json::Value>());
  EXPECT_EQ(expected_special_requirements_json,
            result_special_requirements_json);
}

UTEST(PropositionApplierTest, BuildWaybillProposalBatch) {
  auto segment1 = std::make_shared<united_dispatch::models::Segment>();
  segment1->taxi_classes = {"courier", "express"};
  segment1->taxi_requirements =
      formats::json::FromString(R"({"taxi_req_1": true})");
  handlers::SpecialRequirements sr1{};
  handlers::VirtualTariff vt1{"courier",
                              {handlers::SpecialRequirement{"req1"}}};
  sr1.virtual_tariffs.push_back(vt1);
  segment1->special_requirements = sr1;

  auto segment2 = std::make_shared<united_dispatch::models::Segment>();
  segment2->taxi_classes = {"express", "econom"};
  segment2->taxi_requirements =
      formats::json::FromString(R"({"taxi_req_1": false, "taxi_req_2": true})");
  handlers::SpecialRequirements sr2{};
  handlers::VirtualTariff vt2{"courier",
                              {handlers::SpecialRequirement{"req2"}}};
  sr2.virtual_tariffs.push_back(vt2);
  handlers::VirtualTariff vt3{"express",
                              {handlers::SpecialRequirement{"req1"}}};
  sr2.virtual_tariffs.push_back(vt3);
  segment2->special_requirements = sr2;

  united_dispatch::waybill::WaybillProposal ud_waybill{};
  ud_waybill.segments = {segment1, segment2};
  auto cargo_waybill =
      united_dispatch::waybill::BuildWaybillProposal(ud_waybill);

  auto expected_taxi_order_requirements_extra = formats::json::FromString(R"(
        {"taxi_classes": ["express"], "taxi_req_1": true, "taxi_req_2": true}
    )");
  EXPECT_EQ(cargo_waybill.taxi_order_requirements.extra,
            expected_taxi_order_requirements_extra);

  auto expected_special_requirements_json = formats::json::FromString(R"(
        {
            "virtual_tariffs":[
                {"class":"courier","special_requirements":[{"id":"req1"}, {"id":"req2"}]},
                {"class":"express","special_requirements":[{"id":"req1"}]}
            ]
        }
    )");
  auto result_special_requirements_json = clients::cargo_dispatch::Serialize(
      cargo_waybill.special_requirements,
      formats::serialize::To<formats::json::Value>());
  EXPECT_EQ(expected_special_requirements_json,
            result_special_requirements_json);
}
