#include "classifier.hpp"

#include <gtest/gtest.h>

namespace {

static const std::string kToyotaPriusModel("1");
static const std::string kHyundaiI35Model("2");
static const std::string kAudiA6Model("3");
static const std::string kRenaultLoganModel("4");
static const std::string kVolkswagenTouregModel("5");
static const std::string kNissanTeanaModel("6");
static const std::string kNissanTeanaRModel("7");
static const std::string kAudiA7Model("8");
static const std::string kAudiA8Model("9");
static const std::string kVolkswagenGolfModel("10");
static const std::string kVazKalinaModel("11");
static const std::string kZazChanceModel("12");
}  // anonymous namespace

TEST(RulesForClass, Empty) {
  // Result for classification against empty set of rules should be empty.
  models::dispatch::RulesForClass rules;
  EXPECT_TRUE(rules.Matches(kToyotaPriusModel, 10, 200000));
}

TEST(RulesForClass, HyundaiI35) {
  models::dispatch::RulesForClass rules;
  rules.AddPriceLimit(false, 400000, 5);
  EXPECT_TRUE(rules.Matches(kHyundaiI35Model, 5, 819999));
  EXPECT_FALSE(rules.Matches(kHyundaiI35Model, 6, 819999));
}

TEST(RulesForClass, WhitelistMatches) {
  models::dispatch::RulesForClass rules;
  rules.AddModelToWhitelist(kAudiA6Model, 4);

  // We have no denying rule, so, every model should pass.
  EXPECT_TRUE(rules.Matches(kAudiA6Model, 1, 2000000));
  EXPECT_TRUE(rules.Matches(kAudiA6Model, 4, 2000000));
  EXPECT_TRUE(rules.Matches(kAudiA6Model, 5, 2000000));
  EXPECT_TRUE(rules.Matches(kAudiA6Model, 10, 200000));
  EXPECT_TRUE(rules.Matches(kToyotaPriusModel, 10, 200000));
}

TEST(RulesForClass, WhitelistAndPriceCut) {
  models::dispatch::RulesForClass rules;
  rules.AddModelToWhitelist(kAudiA6Model, 4);
  rules.AddPriceLimit(false, 1000000, 0);  // Deny all.

  // We have no denying rule, so, every model should pass.
  EXPECT_TRUE(rules.Matches(kAudiA6Model, 1, 2000000));
  EXPECT_TRUE(rules.Matches(kAudiA6Model, 4, 2000000));
  EXPECT_FALSE(rules.Matches(kAudiA6Model, 5, 2000000));
  EXPECT_FALSE(rules.Matches(kAudiA6Model, 10, 200000));
  EXPECT_FALSE(rules.Matches(kToyotaPriusModel, 10, 200000));
}

TEST(RulesForClass, WritelistWithMultipleItems) {
  models::dispatch::RulesForClass rules;
  rules.AddModelToWhitelist(kAudiA6Model, 4);
  rules.AddModelToWhitelist(kVolkswagenTouregModel, 3);
  rules.AddModelToWhitelist(kNissanTeanaModel, 2);
  rules.AddPriceLimit(false, 1000000, 0);  // Deny all.

  EXPECT_TRUE(rules.Matches(kAudiA6Model, 0, 2000000));
  EXPECT_TRUE(rules.Matches(kAudiA6Model, 1, 2000000));
  EXPECT_TRUE(rules.Matches(kAudiA6Model, 4, 2000000));
  EXPECT_FALSE(rules.Matches(kAudiA6Model, 5, 2000000));

  EXPECT_TRUE(rules.Matches(kVolkswagenTouregModel, 0, 2000000));
  EXPECT_TRUE(rules.Matches(kVolkswagenTouregModel, 3, 2000000));
  EXPECT_FALSE(rules.Matches(kVolkswagenTouregModel, 4, 2000000));

  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 0, 2000000));
  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 2, 2000000));
  EXPECT_FALSE(rules.Matches(kNissanTeanaModel, 3, 2000000));

  EXPECT_FALSE(rules.Matches(kNissanTeanaRModel, 0, 2000000));
  EXPECT_FALSE(rules.Matches(kAudiA7Model, 0, 2000000));
  EXPECT_FALSE(rules.Matches(kAudiA8Model, 0, 2000000));
  EXPECT_FALSE(rules.Matches(kVolkswagenGolfModel, 0, 2000000));
}

TEST(RulesForClass, PriceFilterOneRule) {
  models::dispatch::RulesForClass rules;
  rules.AddPriceLimit(false, 100000, 5);
  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 0, 2000000));
  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 4, 100001));
  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 5, 100000));
  EXPECT_FALSE(rules.Matches(kNissanTeanaModel, 6, 99999));
  EXPECT_FALSE(rules.Matches(kNissanTeanaModel, 0, 99999));
  EXPECT_FALSE(rules.Matches(kNissanTeanaModel, 10, 50000));
}

TEST(RulesForClass, PriceFilter) {
  models::dispatch::RulesForClass rules;
  rules.AddPriceLimit(false, 100000, 5);
  rules.AddPriceLimit(true, 80000, 2);
  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 0, 2000000));
  EXPECT_FALSE(rules.Matches(kNissanTeanaModel, 5, 90000));
  EXPECT_FALSE(rules.Matches(kNissanTeanaModel, 3, 90000));
  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 2, 90000));
  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 2, 80000));
  EXPECT_FALSE(rules.Matches(kNissanTeanaModel, 2, 70000));
}

TEST(RulesForClass, Blacklist) {
  models::dispatch::RulesForClass rules;
  rules.AddModelToBlacklist(kVazKalinaModel, 3);
  EXPECT_TRUE(rules.Matches(kNissanTeanaModel, 0, 2000000));
  EXPECT_TRUE(rules.Matches(kZazChanceModel, 50, 200));
  EXPECT_TRUE(rules.Matches(kVazKalinaModel, 0, 2000000));
  EXPECT_TRUE(rules.Matches(kVazKalinaModel, 2, 2000000));
  EXPECT_TRUE(rules.Matches(kVazKalinaModel, 3, 2000000));
  EXPECT_FALSE(rules.Matches(kVazKalinaModel, 5, 2000000));
}
