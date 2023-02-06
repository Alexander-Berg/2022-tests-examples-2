#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <fstream>
#include <models/order.hpp>
#include <models/tariff_settings.hpp>
#include <mongo/mongo.hpp>
#include <orderkit/calcinfo_processing.hpp>
#include <utils/bson_utils.hpp>
#include <utils/requirements_serializer.hpp>

namespace orderkit {
namespace calcinfo_internal {

using Requirements = models::requirements::Requirements;
using ClassesRequirements = models::requirements::ClassesRequirements;

bool RequirementsEqual(
    const Requirements& request_requirements,
    const ClassesRequirements& offer_classes_requirements,
    const models::requirements::Descriptions& requirements_descriptions,
    const models::Classes& classes, const LogExtra& log_extra);

}  // namespace calcinfo_internal
}  // namespace orderkit

using namespace orderkit;
using namespace orderkit::calcinfo_internal;
using namespace models::requirements;

class ReqsEqualTest : public ::testing::Test {
 protected:
  Descriptions descriptions;
  std::vector<std::pair<bool, Order>> orders{};
  std::vector<std::pair<bool, Order>> orders_multiclass{};

  void SetUp() override {
    descriptions = [] {
      Description nonts_req;
      nonts_req.name = "animaltransport";
      nonts_req.tariff_specific = false;
      Description ts_req;
      ts_req.name = "childchair_v2";
      ts_req.tariff_specific = true;
      return Descriptions{std::move(nonts_req), std::move(ts_req)};
    }();

    Order order;
    order.request.classes = {"econom"};
    order.request.requirements = {{"animaltransport", true}};
    // positive test
    orders.emplace_back(true, order);

    order.request.classes = {"child_tariff"};
    order.request.requirements = {};
    // negative test: extra non-ts requirement in child_tariff
    orders.emplace_back(false, order);

    order.request.classes = {"econom", "child_tariff"};
    // positive: no reqs in multiclass
    orders_multiclass.emplace_back(true, order);
  }

  void CheckOrder(const Order& order, const mongo::BSONElement& offer,
                  bool expected) {
    ASSERT_EQ(
        expected,
        RequirementsEqual(order.request.requirements,
                          utils::requirements::ParseClassesRequirements(
                              offer["classes_requirements"]),
                          descriptions, order.request.classes, {}  // log_extra
                          ));
  }
};

TEST_F(ReqsEqualTest, SingleClass) {
  auto data = bson_utils::Load("reqs_equal_single_class.json");
  ASSERT_FALSE(data.isEmpty());

  for (const auto& offer : data["offers"].Array()) {
    auto data = utils::mongo::ToDocument(offer);

    for (auto& [expected, order] : orders) {
      const std::string& offer_id = utils::mongo::ToString(data["_id"]);
      std::cout << "***** TEST " << offer_id << " "
                << (expected ? "positive" : "negative") << " ****" << std::endl;
      CheckOrder(order, offer, expected);
    }
  }
}

TEST_F(ReqsEqualTest, Multiclass) {
  auto data = bson_utils::Load("reqs_equal_multiclass.json");
  ASSERT_FALSE(data.isEmpty());

  for (const auto& offer : data["offers"].Array()) {
    auto data = utils::mongo::ToDocument(offer);

    for (auto& [expected, order] : orders_multiclass) {
      const std::string& offer_id = utils::mongo::ToString(data["_id"]);
      std::cout << "***** TEST " << offer_id << " "
                << (expected ? "positive" : "negative") << " ****" << std::endl;
      CheckOrder(order, offer, expected);
    }
  }
}
