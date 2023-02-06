#include "host_counters.hpp"

#include <gtest/gtest.h>

namespace {

models::Counters SyncDownstream(models::HostCounters& host,
                                const std::string& child,
                                const models::Counters& child_counters) {
  host.UpdateDownstream(child, child_counters);
  return host.GetChildOtherTotal(child_counters);
}

models::Counters SyncDownstreamReset(models::HostCounters& host,
                                     const std::string& child,
                                     const models::Counters& child_counters) {
  host.ResetDownstream(child, child_counters);
  return host.GetChildOtherTotal(child_counters);
}

}  // namespace

TEST(HostCounters, SimpleCounters) {
  models::HostCounters proxy;

  EXPECT_EQ(SyncDownstream(proxy, "worker1", {{"path1", {{"c1", 1}}}}),
            (models::Counters{{"path1", {{"c1", 0}}}}));
  EXPECT_EQ(SyncDownstream(proxy, "worker2", {{"path1", {{"c1", 5}}}}),
            (models::Counters{{"path1", {{"c1", 1}}}}));
  EXPECT_EQ(proxy.GetSelfTotal(), (models::Counters{{"path1", {{"c1", 6}}}}));
  EXPECT_EQ(proxy.GetOtherTotal(), (models::Counters{}));

  EXPECT_EQ(SyncDownstream(proxy, "worker1", {{"path1", {{"c1", 3}}}}),
            (models::Counters{{"path1", {{"c1", 5}}}}));
  EXPECT_EQ(SyncDownstream(proxy, "worker2", {{"path1", {{"c1", 8}}}}),
            (models::Counters{{"path1", {{"c1", 3}}}}));
  EXPECT_EQ(proxy.GetSelfTotal(), (models::Counters{{"path1", {{"c1", 11}}}}));
  EXPECT_EQ(proxy.GetOtherTotal(), (models::Counters{}));
}

TEST(HostCounters, ComplexCounters) {
  models::HostCounters proxy;

  models::Counters worker1_self = {
      {"path1", {{"c1", 1}, {"c2", 2}}},
      {"path2", {{"c1", 3}}},
  };
  proxy.UpdateDownstream("worker1", worker1_self);
  auto worker1_other = proxy.GetChildOtherTotal(worker1_self);
  EXPECT_EQ(worker1_other, (models::Counters{
                               {"path1", {{"c1", 0}, {"c2", 0}}},
                               {"path2", {{"c1", 0}}},
                           }));

  models::Counters worker2_self = {
      {"path1", {{"c1", 5}, {"c3", 6}}},
      {"path3", {{"c1", 3}}},
  };
  proxy.UpdateDownstream("worker2", worker2_self);
  auto worker2_other = proxy.GetChildOtherTotal(worker2_self);
  EXPECT_EQ(worker2_other, (models::Counters{
                               {"path1", {{"c1", 1}, {"c2", 2}, {"c3", 0}}},
                               {"path3", {{"c1", 0}}},
                           }));

  EXPECT_EQ(proxy.GetSelfTotal(),
            (models::Counters{
                {"path1", {{"c1", 6}, {"c2", 2}, {"c3", 6}}},
                {"path2", {{"c1", 3}}},
                {"path3", {{"c1", 3}}},
            }));
  EXPECT_EQ(proxy.GetOtherTotal(), (models::Counters{}));

  models::Add(worker1_self, {
                                {"path1", {{"c4", 2}}},
                                {"path3", {{"c2", 1}}},
                            });
  proxy.UpdateDownstream("worker1", worker1_self);
  worker1_other = proxy.GetChildOtherTotal(worker1_self);
  EXPECT_EQ(worker1_other,
            (models::Counters{
                {"path1", {{"c1", 5}, {"c2", 0}, {"c3", 6}, {"c4", 0}}},
                {"path2", {{"c1", 0}}},
                {"path3", {{"c1", 3}, {"c2", 0}}},
            }));

  models::Add(worker2_self, {
                                {"path1", {{"c1", 3}}},
                                {"path2", {{"c2", 3}}},
                            });
  proxy.UpdateDownstream("worker2", worker2_self);
  worker2_other = proxy.GetChildOtherTotal(worker2_self);
  EXPECT_EQ(worker2_other,
            (models::Counters{
                {"path1", {{"c1", 1}, {"c2", 2}, {"c3", 0}, {"c4", 2}}},
                {"path2", {{"c1", 3}, {"c2", 0}}},
                {"path3", {{"c1", 0}, {"c2", 1}}},
            }));

  EXPECT_EQ(proxy.GetSelfTotal(),
            (models::Counters{
                {"path1", {{"c1", 9}, {"c2", 2}, {"c3", 6}, {"c4", 2}}},
                {"path2", {{"c1", 3}, {"c2", 3}}},
                {"path3", {{"c1", 3}, {"c2", 1}}},
            }));
  EXPECT_EQ(proxy.GetOtherTotal(), (models::Counters{}));
}

TEST(HostCounters, UpstreamUpdate) {
  models::HostCounters proxy;

  SyncDownstream(proxy, "worker1", {{"path1", {{"c1", 1}}}});
  SyncDownstream(proxy, "worker2", {{"path1", {{"c1", 5}}}});

  const models::Counters upstream_response{
      {"path1", {{"c1", 100}, {"c2", 50}}}};
  proxy.UpdateUpstream(upstream_response);
  EXPECT_EQ(proxy.GetOtherTotal(), upstream_response);

  EXPECT_EQ(SyncDownstream(proxy, "worker1", {{"path1", {{"c1", 3}}}}),
            (models::Counters{{"path1", {{"c1", 105}, {"c2", 50}}}}));
  EXPECT_EQ(SyncDownstream(proxy, "worker2", {{"path1", {{"c1", 7}}}}),
            (models::Counters{{"path1", {{"c1", 103}, {"c2", 50}}}}));
  EXPECT_EQ(proxy.GetSelfTotal(), (models::Counters{{"path1", {{"c1", 10}}}}));
  EXPECT_EQ(proxy.GetOtherTotal(), upstream_response);
}

TEST(HostCounters, DownstreamReset) {
  models::HostCounters proxy;

  int64_t w1_c1 = 1;
  int64_t w2_c1 = 5;

  SyncDownstream(proxy, "w1", {{"path1", {{"c1", w1_c1}}}});
  SyncDownstream(proxy, "w2", {{"path1", {{"c1", w2_c1}}}});
  EXPECT_EQ(proxy.GetSelfTotal(),
            (models::Counters{{"path1", {{"c1", w1_c1 + w2_c1}}}}));

  const int64_t w1_reset_diff = 2;
  w1_c1 += w1_reset_diff;
  EXPECT_EQ(SyncDownstreamReset(proxy, "w1", {{"path1", {{"c1", w1_c1}}}}),
            (models::Counters{{"path1", {{"c1", w2_c1 - w1_reset_diff}}}}));
  EXPECT_EQ(
      proxy.GetSelfTotal(),
      (models::Counters{{"path1", {{"c1", w1_c1 + w2_c1 - w1_reset_diff}}}}));

  w1_c1 += 1;
  EXPECT_EQ(SyncDownstream(proxy, "w1", {{"path1", {{"c1", w1_c1}}}}),
            (models::Counters{{"path1", {{"c1", w2_c1 - w1_reset_diff}}}}));
  w2_c1 += 2;
  EXPECT_EQ(SyncDownstream(proxy, "w2", {{"path1", {{"c1", w2_c1}}}}),
            (models::Counters{{"path1", {{"c1", w1_c1 - w1_reset_diff}}}}));
  EXPECT_EQ(
      proxy.GetSelfTotal(),
      (models::Counters{{"path1", {{"c1", w1_c1 + w2_c1 - w1_reset_diff}}}}));
}

TEST(HostCounters, CollectGarbageDownstream) {
  models::HostCounters proxy;

  SyncDownstream(proxy, "w1",
                 {{"path1", {{"c1", 99}, {"c2", 100}, {"c3", 200}}}});
  SyncDownstream(proxy, "w2",
                 {{"path1", {{"c1", 99}, {"c2", 100}, {"c3", 200}}}});

  SyncDownstream(proxy, "w1", {{"path1", {{"c2", 100}}}});
  SyncDownstream(proxy, "w2", {{"path1", {}}});

  const auto collected = proxy.CollectGarbage(
      {{"path1", {{"c1", 220}, {"c2", 220}, {"c3", 220}}}});
  EXPECT_EQ(collected, 1);
  EXPECT_EQ(proxy.GetSelfTotal(),
            (models::Counters{{"path1", {{"c2", 200}, {"c3", 400}}}}));
}

TEST(HostCounters, CollectGarbageUpstream) {
  models::HostCounters proxy;

  models::Counters downstream{{"path1", {{"c1", 1}, {"c2", 2}}}};
  SyncDownstream(proxy, "w1", downstream);

  models::Counters upstream{{"path1", {{"c2", 222}, {"c3", 333}}}};
  proxy.UpdateUpstream(upstream);

  EXPECT_EQ(proxy.GetSelfTotal(), downstream);
  EXPECT_EQ(proxy.GetOtherTotal(), upstream);
  EXPECT_EQ(proxy.GetChildTotal("w1"), downstream);

  downstream = {{"path1", {{"c2", 22}}}};
  SyncDownstream(proxy, "w1", downstream);

  EXPECT_EQ(proxy.GetSelfTotal(),
            (models::Counters{{"path1", {{"c1", 1}, {"c2", 22}}}}));
  EXPECT_EQ(proxy.GetOtherTotal(), upstream);
  EXPECT_EQ(proxy.GetChildTotal("w1"), downstream);

  auto collected =
      proxy.CollectGarbage({{"path1", {{"c1", 100}, {"c2", 200}}}});
  EXPECT_EQ(collected, 2);

  EXPECT_EQ(proxy.GetSelfTotal(), (models::Counters{{"path1", {{"c2", 22}}}}));
  EXPECT_EQ(proxy.GetOtherTotal(),
            (models::Counters{{"path1", {{"c2", 222}}}}));
  EXPECT_EQ(proxy.GetChildTotal("w1"), downstream);

  SyncDownstream(proxy, "w1", {});

  EXPECT_EQ(proxy.GetSelfTotal(), (models::Counters{{"path1", {{"c2", 22}}}}));
  EXPECT_EQ(proxy.GetOtherTotal(),
            (models::Counters{{"path1", {{"c2", 222}}}}));
  EXPECT_EQ(proxy.GetChildTotal("w1"), models::Counters());

  collected = proxy.CollectGarbage({{"path1", {{"c2", 400}}}});
  EXPECT_EQ(collected, 1);
  EXPECT_EQ(proxy.GetSelfTotal(), models::Counters());
  EXPECT_EQ(proxy.GetOtherTotal(), models::Counters());
  EXPECT_EQ(proxy.GetChildTotal("w1"), models::Counters());
}

TEST(HostCounters, CollectGarbageDownstreamReset) {
  models::HostCounters proxy;

  models::Counters w1{{"path1", {{"c1", 153}, {"c2", 222}}}};
  SyncDownstream(proxy, "w1", w1);

  models::Counters w2{{"path1", {{"c1", 351}}}};
  SyncDownstream(proxy, "w2", w2);

  auto self_total = w1;
  models::Add(self_total, w2);
  EXPECT_EQ(proxy.GetSelfTotal(), self_total);
  EXPECT_EQ(proxy.GetChildTotal("w1"), w1);
  EXPECT_EQ(proxy.GetChildTotal("w2"), w2);

  auto collected =
      proxy.CollectGarbage({{"path1", {{"c1", 1000}, {"c2", 1000}}}});
  EXPECT_EQ(collected, 0);
  EXPECT_EQ(proxy.GetSelfTotal(), self_total);
  EXPECT_EQ(proxy.GetChildTotal("w1"), w1);
  EXPECT_EQ(proxy.GetChildTotal("w2"), w2);

  w1.clear();
  proxy.ResetDownstream("w1", w1);
  EXPECT_EQ(proxy.GetChildTotal("w1"), w1);

  collected = proxy.CollectGarbage({{"path1", {{"c1", 1000}, {"c2", 1000}}}});
  EXPECT_EQ(collected, 1);
  EXPECT_EQ(proxy.GetSelfTotal(),
            (models::Counters{{"path1", {{"c1", 153 + 351}}}}));
  EXPECT_EQ(proxy.GetChildTotal("w1"), w1);
  EXPECT_EQ(proxy.GetChildTotal("w2"), w2);

  w2.clear();
  proxy.ResetDownstream("w2", w2);
  EXPECT_EQ(proxy.GetChildTotal("w2"), w2);

  collected = proxy.CollectGarbage({{"path1", {{"c1", 1000}}}});
  EXPECT_EQ(collected, 1);
  EXPECT_EQ(proxy.GetSelfTotal(), models::Counters());
  EXPECT_EQ(proxy.GetChildTotal("w1"), w1);
  EXPECT_EQ(proxy.GetChildTotal("w2"), w2);
}
