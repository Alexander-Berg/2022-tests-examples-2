#include <gtest/gtest.h>

#include "fetch_payment_methods.hpp"

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_park_activation/fetch_park_activation.hpp>

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;
namespace dpt = driver_payment_type;

using cf::Result;

static cf::FilterInfo kEmptyInfo;

class FetchPaymentMethodsTest : public testing::Test {
 protected:
  void SetUp() override {
    // Parks
    parks = std::make_shared<
        std::unordered_map<std::string, parks_activation::models::Park>>();
    AddPark("clid1", true, true);
    AddPark("clid2", true);

    // Drivers
    drivers = std::make_shared<models::Drivers>(
        [](const std::string&) { return models::DriverPtr{}; });
    driver_payment_types = std::make_shared<models::DriverPaymentTypes>();

    AddProfile("dbid1_uuid1", "license1", dpt::Type::kNone, false);    // any
    AddProfile("dbid1_uuid2", "license2", dpt::Type::kOnline, false);  // card
    AddProfile("dbid1_uuid3", "license3", dpt::Type::kNone, true);     // card
    AddProfile("dbid1_uuid4", "license4", dpt::Type::kCash, false);    // cash
    AddProfile("dbid2_uuid5", "license5", dpt::Type::kOnline, false);  // cash
  }

  void AddPark(const std::string& clid, bool cash = false, bool card = false,
               bool corp = false, bool coupon = false) {
    auto park = parks_activation::models::Park{};
    park.park_id = clid;
    park.can_cash = cash;
    park.can_card = card;
    park.can_corp = corp;
    park.can_coupon = coupon;

    parks->emplace(clid, park);
  }

  void AddProfile(const std::string& dbid_uuid, const std::string& license,
                  const dpt::Type& payment_type, const bool only_cards) {
    auto driver = std::make_shared<models::Driver>();
    driver->id = models::DriverId::FromDbidUuid(dbid_uuid);
    driver->license_id = license;
    drivers->Insert(dbid_uuid, models::DriverPtr(driver));
    driver_payment_types->insert({license, {payment_type, 0}});
    if (only_cards) driver->balance_limit = 10;
  }

  cf::Context& GetContext(const std::string& driver_id) {
    context.ClearData();

    const auto& id = models::DriverId::FromDbidUuid(driver_id);
    std::string clid = (id.dbid == "dbid1") ? "clid1" : "clid2";

    cfi::FetchDriver::Set(context,
                          drivers->Find(driver_id, models::Drivers::kCache));
    cfi::FetchParkActivation::Set(context, parks->at(clid));
    return context;
  }

  std::shared_ptr<
      std::unordered_map<std::string, parks_activation::models::Park>>
      parks;
  std::shared_ptr<models::ZoneSettings> zones;
  std::shared_ptr<models::Drivers> drivers;
  std::shared_ptr<models::DriverPaymentTypes> driver_payment_types;
  bool allow_onlycard{false};
  cf::Context context;
};

TEST_F(FetchPaymentMethodsTest, Zone1) {
  cfi::FetchPaymentMethods filter(kEmptyInfo, true, driver_payment_types,
                                  allow_onlycard);
  candidates::GeoMember member;
  {
    auto& context = GetContext("dbid1_uuid1");
    member.id = "dbid1_uuid1";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 2);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCash) != 0);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCard) != 0);
  }
  {
    auto& context = GetContext("dbid1_uuid2");
    member.id = "dbid1_uuid2";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 1);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCard) != 0);
  }
  {
    auto& context = GetContext("dbid1_uuid3");
    member.id = "dbid1_uuid3";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 1);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCard) != 0);
  }
  {
    auto& context = GetContext("dbid1_uuid4");
    member.id = "dbid1_uuid4";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 1);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCash) != 0);
  }
  {
    auto& context = GetContext("dbid2_uuid5");
    member.id = "dbid1_uuid5";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 1);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCash) != 0);
  }
}

TEST_F(FetchPaymentMethodsTest, Zone2) {
  cfi::FetchPaymentMethods filter(kEmptyInfo, false, driver_payment_types,
                                  allow_onlycard);
  candidates::GeoMember member;
  {
    auto& context = GetContext("dbid1_uuid1");
    member.id = "dbid1_uuid1";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 2);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCash) != 0);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCard) != 0);
  }
  {
    auto& context = GetContext("dbid1_uuid2");
    member.id = "dbid1_uuid2";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 2);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCash) != 0);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCard) != 0);
  }
  {
    auto& context = GetContext("dbid1_uuid3");
    member.id = "dbid1_uuid3";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 1);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCard) != 0);
  }
  {
    auto& context = GetContext("dbid1_uuid4");
    member.id = "dbid1_uuid4";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 1);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCash) != 0);
  }
  {
    auto& context = GetContext("dbid2_uuid5");
    member.id = "dbid1_uuid5";
    filter.Process(member, context);
    const auto& result = cfi::FetchPaymentMethods::Get(context);
    ASSERT_EQ(result.size(), 1);
    EXPECT_TRUE(result.count(dpt::OrderPaymentType::kCash) != 0);
  }
}
