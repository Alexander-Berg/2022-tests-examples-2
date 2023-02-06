#include <gtest/gtest.h>

#include <common/include/counters.h>
#include <common/include/sharded_counter.h>

namespace maps::rate_limiter2::tests {

namespace {

// The way changes propagated upstream
template <typename T>
void PropagateChanges(ShardedCounter<T>& child, ShardedCounter<T>& parent) {
  const auto& update = child.shardTotal();
  parent.downstreamUpdate(child.id(), update);
  child.otherTotal() = parent.downstreamResponse(update);
}

}  // anonymous namespace

TEST(ShardedCounter, SingleCounter) {
  using CountersType = impl::AdditiveMap<std::string, int>;  // <id, value>
  ShardedCounter<CountersType> worker1("w1"), worker2("w2"), proxy("proxy"),
      server("srv");

  worker1.shardTotal() += CountersType({{"c1", 1}});
  worker2.shardTotal() += CountersType({{"c1", 5}});

  PropagateChanges(worker1, proxy);  // w1 -> proxy

  PropagateChanges(worker2, proxy);  // w2 -> proxy

  PropagateChanges(proxy, server);  // proxy -> server

  // check workers state
  EXPECT_EQ(worker1.shardTotal(), CountersType({{"c1", 1}}));
  EXPECT_EQ(worker1.otherTotal(),
            CountersType({{"c1", 0}}));  // worker1 sync was before worker2

  EXPECT_EQ(worker2.shardTotal(), CountersType({{"c1", 5}}));
  EXPECT_EQ(worker2.otherTotal(), CountersType({{"c1", 1}}));

  {  // check proxy state
    EXPECT_EQ(proxy.shardTotal(), CountersType({{"c1", 6}}));
    EXPECT_EQ(proxy.otherTotal(), CountersType({{"c1", 0}}));
    EXPECT_EQ(proxy.childCounters("w1"), CountersType({{"c1", 1}}));
    EXPECT_EQ(proxy.childCounters("w2"), CountersType({{"c1", 5}}));
  }

  {  // check server state
    EXPECT_EQ(server.shardTotal(), CountersType({{"c1", 6}}));
    EXPECT_EQ(server.otherTotal(), CountersType());
    EXPECT_EQ(server.childCounters("proxy"), CountersType({{"c1", 6}}));
  }
}

TEST(ShardedCounter, ComplexCounter) {
  const auto client1 = "client.1";
  const auto client2 = "client.2";

  ShardedCounter<> worker1("w1"), worker2("w2"), proxy("proxy");

  auto upd1 = Counters(
      {{"resource.1", {{client1, 1}}}, {"resource.2", {{client2, 2}}}});

  worker1.shardTotal() += upd1;

  auto upd2 = Counters({{"resource.1", {{client1, 2}, {client2, 1}}},
                        {"resource.2", {{client1, 1}}}});
  worker2.shardTotal() += upd2;

  PropagateChanges(worker1, proxy);  // w1 -> proxy

  PropagateChanges(worker2, proxy);  // w2 -> proxy

  PropagateChanges(worker1, proxy);  // w1 -> proxy again (to receive w2 update)

  // check workers state
  EXPECT_EQ(worker1.shardTotal(), upd1);
  EXPECT_EQ(worker1.otherTotal(),
            upd1 + upd2 - upd1);  // worker1 sync was before worker2

  EXPECT_TRUE(worker2.shardTotal() == upd2);
  {
    // NB: currently (upd1+upd2-upd2 != upd1) 'cause zero counters not dropped
    // (see Counters type)
    EXPECT_EQ(worker2.otherTotal(), upd1 + upd2 - upd2);
  }

  EXPECT_TRUE(worker1.shardTotal() + worker1.otherTotal() ==
              worker2.shardTotal() + worker2.otherTotal());
  EXPECT_TRUE(worker1.shardTotal() + worker1.otherTotal() == upd1 + upd2);

  {  // check proxy state
    EXPECT_TRUE(proxy.shardTotal() == upd1 + upd2);
    EXPECT_TRUE(proxy.otherTotal() == Counters());
    EXPECT_EQ(proxy.childCounters("w1"), upd1);
    EXPECT_EQ(proxy.childCounters("w2"), upd2);
  }
}

TEST(ShardedCounter, ComplexCounterFiltering) {
  auto client1 = "client.1";
  auto shardTotal = Counters(
      {{"resource.1", {{client1, 1}}}, {"resource.2", {{client1, 1}}}});
  auto otherTotal = Counters(
      {{"resource.1", {{client1, 2}}}, {"resource.3", {{client1, 2}}}});
  auto update = Counters(
      {{"resource.1", {{client1, 10}}}, {"resource.4", {{client1, 10}}}});

  // resource filtering - reply contain only resources mentioned in request
  ShardedCounter<> node("n1", shardTotal, ShardedCounter<>::Registry(),
                        otherTotal);

  node.downstreamUpdate("child", update);
  auto reply = node.downstreamResponse(update);
  EXPECT_EQ(reply, Counters({{"resource.1", {{client1, 3}}},
                             {"resource.4", {{client1, 0}}}}));

  EXPECT_EQ(node.shardTotal(), Counters({{"resource.1", {{client1, 11}}},
                                         {"resource.2", {{client1, 1}}},
                                         {"resource.4", {{client1, 10}}}}));
  EXPECT_EQ(node.otherTotal(), otherTotal);
}

TEST(ShardedCounter, DownstreamReset) {
  const auto client = "client1";

  ShardedCounter<Counters> C("test");

  auto A = 2000;  // starting values
  auto B = 1000;

  C.downstreamUpdate("A", Counters{{"resource", {{{client, A}}}}});
  C.downstreamUpdate("B", Counters{{"resource", {{{client, B}}}}});

  // check what we got
  EXPECT_EQ(C.shardTotal(), Counters({{"resource", {{client, A + B}}}}));
  EXPECT_EQ(C.childCounters("A"), Counters({{"resource", {{client, A}}}}));
  EXPECT_EQ(C.childCounters("B"), Counters({{"resource", {{client, B}}}}));

  // no updates from A (A lost connection), but B still here
  B += 100;
  C.downstreamUpdate("B", Counters{{"resource", {{{client, B}}}}});

  A += 500;
  // A is back bu late, so we reset before update
  C.downstreamReset("A", Counters{{"resource", {{{client, A}}}}});
  auto reply = C.downstreamResponse(Counters{{"resource", {{{client, A}}}}});
  EXPECT_EQ(reply, Counters({{"resource", {{client, B - 500}}}}));

  B += 100;  // B expects no A delta in reply
  C.downstreamUpdate("B", Counters{{"resource", {{{client, B}}}}});
  reply = C.downstreamResponse(Counters{{"resource", {{{client, B}}}}});
  EXPECT_EQ(reply, Counters({{"resource", {{client, A - 500}}}}));

  // check state after Reset
  EXPECT_EQ(C.shardTotal(), Counters({{"resource", {{client, A + B - 500}}}}));
  EXPECT_EQ(C.childCounters("A"), Counters({{"resource", {{client, A}}}}));
  EXPECT_EQ(C.childCounters("B"), Counters({{"resource", {{client, B}}}}));

  // now comtinue as usual
  A += 20;
  C.downstreamUpdate("A", Counters{{"resource", {{{client, A}}}}});
  reply = C.downstreamResponse(Counters{{"resource", {{{client, A}}}}});
  EXPECT_EQ(reply, Counters({{"resource", {{client, B - 500}}}}));
  B += 10;
  C.downstreamUpdate("B", Counters{{"resource", {{{client, B}}}}});
  reply = C.downstreamResponse(Counters{{"resource", {{{client, B}}}}});
  EXPECT_EQ(reply, Counters({{"resource", {{client, A - 500}}}}));

  // final state check
  EXPECT_EQ(C.shardTotal(), Counters({{"resource", {{client, A + B - 500}}}}));
  EXPECT_EQ(C.childCounters("A"), Counters({{"resource", {{client, A}}}}));
  EXPECT_EQ(C.childCounters("B"), Counters({{"resource", {{client, B}}}}));
}

TEST(ShardedCounter, DownstreamResetToSmallerValue) {
  const auto client = "client1";

  ShardedCounter<Counters> C("test");

  auto A0 = Counters{{"resource", {{{client, 100}}}}};
  auto B = Counters{{"resource", {{{client, 10}}}}};
  C.downstreamUpdate("A", A0);
  C.downstreamUpdate("B", B);

  // Assume A lost connection and garbage collected counters
  auto A1 = Counters{{"resource", {{{client, 1}}}}};  // now A value is smaller
  // and sync is late, so we reset before update
  C.downstreamReset("A", A1);
  auto reply = C.downstreamResponse(A1);
  EXPECT_EQ(reply, A0 + B - A1);

  B += Counters{{"resource", {{{client, 10}}}}};  // B += 10
  C.downstreamUpdate("B", B);
  reply = C.downstreamResponse(B);
  EXPECT_EQ(reply, A0);  // 'cause total is same after A reset/update

  // final state check
  EXPECT_EQ(C.shardTotal(), A0 + B);
  EXPECT_EQ(C.childCounters("A"), A1);
  EXPECT_EQ(C.childCounters("B"), B);
}

}  // namespace maps::rate_limiter2::tests
