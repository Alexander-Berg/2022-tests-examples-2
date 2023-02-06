#include <userver/utest/utest.hpp>

#include "blocklist.hpp"
#include "common_fixture.hpp"

namespace {

namespace bf = blocklist_fixture;
namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

const auto kParkId_1 = "park_1";
const auto kParkId_2 = "park_2";
const auto kLicenseId_1 = "license_1";
const auto kLicenseId_2 = "license_2";
const auto kCarNumber_1 = "number_1";
const auto kCarNumber_2 = "number_2";
const auto kCarId_1 = "car_1";
const auto kUuid_1 = "uuid_1";
const auto kBlockId_1 = "id_1";
}  // namespace

UTEST(BlocklistTest, ParkIdCarNumber) {
  auto cache = bf::CreateCache();
  cache->ProcessNewBlocks({bf::CreateItem(
      kBlockId_1, {bf::kParkId, bf::kCarNumber}, {kParkId_1, kCarNumber_1},
      {false, true}, bf::kParkIdCarNumberPredicate)});
  cf::partners::Blocklist filter(kEmptyInfo, cache);
  candidates::GeoMember member;

  auto context = bf::CreateContext(kParkId_1, kCarNumber_1, kLicenseId_1,
                                   kCarId_1, kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);

  // change target entity's car number
  context = bf::CreateContext(kParkId_1, kCarNumber_2, kLicenseId_1, kCarId_1,
                              kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  // get number back, but change the park
  context = bf::CreateContext(kParkId_2, kCarNumber_1, kLicenseId_1, kCarId_1,
                              kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

UTEST(BlocklistTest, ParkIdLicenseId) {
  auto cache = bf::CreateCache();
  cache->ProcessNewBlocks({bf::CreateItem(
      kBlockId_1, {bf::kParkId, bf::kLicenseId}, {kParkId_1, kLicenseId_1},
      {false, true}, bf::kParkIdLicenseIdPredicate)});

  cf::partners::Blocklist filter(kEmptyInfo, cache);
  candidates::GeoMember member;

  auto context = bf::CreateContext(kParkId_1, kCarNumber_1, kLicenseId_1,
                                   kCarId_1, kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);

  // change target entity's license
  context = bf::CreateContext(kParkId_1, kCarNumber_1, kLicenseId_2, kCarId_1,
                              kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  // get license back, but change the park
  context = bf::CreateContext(kParkId_2, kCarNumber_1, kLicenseId_1, kCarId_1,
                              kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

UTEST(BlocklistTest, CarNumber) {
  auto cache = bf::CreateCache();
  cache->ProcessNewBlocks(
      {bf::CreateItem(kBlockId_1, {bf::kCarNumber}, {kCarNumber_1}, {true},
                      bf::kCarNumberPredicate)});
  cf::partners::Blocklist filter(kEmptyInfo, cache);
  candidates::GeoMember member;

  auto context = bf::CreateContext(kParkId_1, kCarNumber_1, kLicenseId_1,
                                   kCarId_1, kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);

  // change target entity's car_number
  context = bf::CreateContext(kParkId_1, kCarNumber_2, kLicenseId_1, kCarId_1,
                              kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  // get license back, but change the park
  context = bf::CreateContext(kParkId_2, kCarNumber_1, kLicenseId_1, kCarId_1,
                              kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}

UTEST(BlocklistTest, LicenseId) {
  auto cache = bf::CreateCache();
  cache->ProcessNewBlocks(
      {bf::CreateItem(kBlockId_1, {bf::kLicenseId}, {kLicenseId_1}, {true},
                      bf::kLicenseIdPredicate)});
  cf::partners::Blocklist filter(kEmptyInfo, cache);
  candidates::GeoMember member;

  auto context = bf::CreateContext(kParkId_1, kCarNumber_1, kLicenseId_1,
                                   kCarId_1, kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);

  // change target entity's license
  context = bf::CreateContext(kParkId_1, kCarNumber_1, kLicenseId_2, kCarId_1,
                              kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  // get license back, but change the park
  context = bf::CreateContext(kParkId_2, kCarNumber_1, kLicenseId_1, kCarId_1,
                              kUuid_1);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}
