#include <gtest/gtest.h>

#include <cache/billing_subvention_rules_lru.hpp>

using bs_cache = caches::BillingSubventionRulesLRUCache;
using bsr = bs_cache::ResultCode;
using sec = std::chrono::seconds;

TEST(BillingSubventionRulesLRUCache, Keys) {
  bs_cache cache(1000, sec(60), sec(60));

  using Set = std::unordered_set<std::string>;
  auto begin = utils::datetime::Now();
  auto end = begin + std::chrono::hours(6);

  bs_cache::Result res1{{"1", {}}};
  auto key1 = bs_cache::Input{begin, end, {}, "1"};
  auto key1id = bs_cache::Input{Set{"1"}};
  cache.AddSubventions(key1, res1);
  cache.AddSubventions(key1id, res1);

  bs_cache::Result res2{{"2", {}}};
  auto key2 = bs_cache::Input{begin, end, {}, "2"};
  auto key2id = bs_cache::Input{Set{"2"}};
  cache.AddSubventions(key2, res2);
  cache.AddSubventions(key2id, res2);

  bs_cache::Result res3{{"3", {}}};
  auto key3 = bs_cache::Input{begin, end, {}, "3"};
  auto key3id = bs_cache::Input{Set{"3"}};
  cache.AddSubventions(key3, res3);
  cache.AddSubventions(key3id, res3);

  bs_cache::Result res;
  ASSERT_EQ(cache.GetSubventions(key1, res), bsr::OK);
  ASSERT_EQ(res, res1);
  ASSERT_EQ(cache.GetSubventions(key2, res), bsr::OK);
  ASSERT_EQ(res, res2);
  ASSERT_EQ(cache.GetSubventions(key3, res), bsr::OK);
  ASSERT_EQ(res, res3);

  ASSERT_EQ(cache.GetSubventions(key1id, res), bsr::OK);
  ASSERT_EQ(res, res1);
  ASSERT_EQ(cache.GetSubventions(key2id, res), bsr::OK);
  ASSERT_EQ(res, res2);
  ASSERT_EQ(cache.GetSubventions(key3id, res), bsr::OK);
  ASSERT_EQ(res, res3);
}

TEST(BillingSubventionRulesLRUCache, Hashes) {
  bs_cache cache(1000, sec(60), sec(60));
  using Set = std::unordered_set<std::string>;

  auto begin = utils::datetime::Now();
  auto end = begin + std::chrono::hours(6);

  bs_cache::Result res1{{"1", {}}};
  auto key = bs_cache::Input{begin, end, {"1", "2"}};
  auto key_inv = bs_cache::Input{begin, end, {"2", "1"}};
  auto keyid = bs_cache::Input{Set{"1", "2"}};
  auto keyid_inv = bs_cache::Input{Set{"2", "1"}};
  cache.AddSubventions(key, res1);
  cache.AddSubventions(keyid, res1);

  bs_cache::Result res;
  ASSERT_EQ(cache.GetSubventions(key, res), bsr::OK);
  ASSERT_EQ(res, res1);
  ASSERT_EQ(cache.GetSubventions(key_inv, res), bsr::OK);
  ASSERT_EQ(res, res1);

  ASSERT_EQ(cache.GetSubventions(keyid, res), bsr::OK);
  ASSERT_EQ(res, res1);
  ASSERT_EQ(cache.GetSubventions(keyid_inv, res), bsr::OK);
  ASSERT_EQ(res, res1);
}

TEST(BillingSubventionRulesLRUCache, FindInconsistency) {
  bs_cache cache(1000, sec(60), sec(60));
  auto begin = utils::datetime::Now();
  auto end = begin + std::chrono::hours(6);
  bs_cache::Result res{{"1", {}}, {"2", {}}};

  auto key1 = bs_cache::Input{begin, end, {}, {}};
  cache.AddSubventions(key1, res);

  auto key2 = bs_cache::Input{begin + sec(120), end + sec(120), {}, {}};
  cache.AddSubventions(key2, res);

  auto key3 = bs_cache::Input{begin + sec(220), end + sec(220), {}, {}};
  cache.AddSubventions(key3, res);

  auto key4 = bs_cache::Input{begin + sec(320), end + sec(320), {}, {}};
  cache.AddSubventions(key4, res);

  bs_cache::Result res_invalid{};
  auto key_invalid = bs_cache::Input{begin - sec(120), end - sec(120), {}, {}};
  cache.AddSubventions(key_invalid, res_invalid);

  ASSERT_EQ(cache.GetSubventions(key1, res), bsr::OK);
  ASSERT_EQ(res.size(), 2ull);

  ASSERT_EQ(cache.GetSubventions(key_invalid, res), bsr::OK);
  ASSERT_EQ(res.size(), 0ull);

  ASSERT_EQ(cache.GetSubventions(key2, res), bsr::OK);
  ASSERT_EQ(res.size(), 2ull);

  ASSERT_EQ(cache.GetSubventions(key3, res), bsr::OK);
  ASSERT_EQ(res.size(), 2ull);

  ASSERT_EQ(cache.GetSubventions(key4, res), bsr::OK);
  ASSERT_EQ(res.size(), 2ull);
}

TEST(BillingSubventionRulesLRUCache, TestCore) {
  bs_cache cache(1000, sec(60), sec(60));
  auto begin = utils::datetime::Now();
  auto end = begin + std::chrono::hours(6);
  utils::datetime::MockNowSet(begin);

  bs_cache::Result res;

  auto key1 = bs_cache::Input{begin, end, {}, {}};
  cache.AddSubventions(key1, {{"key1", {}}});

  utils::datetime::MockSleep(sec(30));
  auto key2 = bs_cache::Input{begin + sec(120), end + sec(120), {}, {}};
  cache.AddSubventions(key2, {{"key2", {}}});

  ASSERT_EQ(cache.Size(), 2ull);

  utils::datetime::MockSleep(sec(51));
  auto key3 = bs_cache::Input{begin + sec(220), end + sec(220), {}, {}};
  cache.AddSubventions(key3, {{"key3", {}}});

  auto key4 = bs_cache::Input{begin + sec(220), end + sec(220), {}, {"1"}};
  cache.AddSubventions(key4, {{"key4", {}}});

  auto key5 = bs_cache::Input{begin + sec(220), end + sec(220), {}, {"2"}};
  cache.AddSubventions(key5, {{"key5", {}}});

  ASSERT_EQ(cache.Size(), 4ull);

  ASSERT_EQ(cache.GetSubventions(key3, res), bsr::OK);
  ASSERT_EQ(res.begin()->first, "key3");
  ASSERT_EQ(cache.GetSubventions(key4, res), bsr::OK);
  ASSERT_EQ(res.begin()->first, "key4");
  ASSERT_EQ(cache.GetSubventions(key5, res), bsr::OK);
  ASSERT_EQ(res.begin()->first, "key5");
  ASSERT_EQ(cache.GetSubventions(key2, res), bsr::OK);
  ASSERT_EQ(res.begin()->first, "key2");
}
