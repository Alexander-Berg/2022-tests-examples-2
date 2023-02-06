#include <gtest/gtest.h>

#include <agent/lib/access_limiter.h>

namespace maps::rate_limiter2::agent::tests {

using std::chrono::seconds;
using std::chrono::system_clock;

namespace {

class ManualClock {
  system_clock::time_point t_;

 public:
  ManualClock(system_clock::time_point t = system_clock::now()) : t_(t) {}

  system_clock::time_point operator()() const { return t_; }
  system_clock::time_point& operator()() { return t_; }
};

int64_t toSeconds(system_clock::time_point t) {
  return std::chrono::duration_cast<std::chrono::seconds>(t.time_since_epoch())
      .count();
}

}  // anonymous namespace

TEST(AccessLimiter, Standalone) {
  ManualClock timeMeter;
  AccessLimiter limiter(std::ref(timeMeter));
  LimitsRegistry registry(
      {{"",
        {// 'anybody' limits
         {"resource.1", LimitInfo(5, 5, 1)},
         {"resource.forbidden", LimitInfo(0, 0)}}},  // 'forbidden'
       {"client.1",
        {{"resource.1", LimitInfo(10, 10, 1)},  // specific limits
         {"resource.2", LimitInfo(5, 5, 1)}}}},
      153);
  limiter.resetLimits(std::move(registry));

  // check correct limits version reported
  EXPECT_EQ(limiter.limitsVersion(), 153);

  // test undefined limit
  EXPECT_TRUE(limiter.access("client.1", "", 1));
  EXPECT_TRUE(limiter.access("client.1", "no.such.resource", 1));

  // test explicitly forbidden
  EXPECT_THROW(limiter.access("client.1", "resource.forbidden", 1),
               AccessForbidden);

  // access weight 1
  EXPECT_TRUE(limiter.access("some.client", "resource.1", 1));
  // access weight 4
  EXPECT_TRUE(limiter.access("some.client", "resource.1", 4));
  // access weight 1, expect reject ('anybody' limit applied)
  EXPECT_FALSE(limiter.access("some.client", "resource.1", 1));

  // another client access (higher specific limit applied)
  EXPECT_TRUE(limiter.access("client.1", "resource.1", 10));
  // and it's exceeded too
  EXPECT_FALSE(limiter.access("client.1", "resource.1", 1));

  {  // check counters
    auto expected =
        Counters({{"resource.1", {{"client.1", 10}, {"some.client", 5}}}});
    EXPECT_EQ(limiter.shardCounters(), expected);
  }

  timeMeter() += seconds(1);  // time step

  // allowed weight 5
  EXPECT_TRUE(limiter.access("some.client", "resource.1", 5));

  // client1 is good too
  EXPECT_TRUE(limiter.access("client.1", "resource.1", 5));
  // and for resource2
  EXPECT_TRUE(limiter.access("client.1", "resource.2", 5));
  // limits exceeded
  EXPECT_FALSE(limiter.access("client.1", "resource.2", 1));

  {  // check counters
    auto expected =
        Counters({{"resource.1", {{"client.1", 15}, {"some.client", 10}}},
                  {"resource.2", {{"client.1", 5}}}});
    EXPECT_EQ(limiter.shardCounters(), expected);
  }
}

TEST(AccessLimiter, UpdateExternal) {
  ManualClock timeMeter;  //(10);
  AccessLimiter limiter(std::ref(timeMeter));
  LimitsRegistry registry(
      {
          {"",
           {{"resource.1",
             LimitInfo(10, 10, 1)}}}  // 'anybody' limit to resource 3
      },
      1);
  limiter.resetLimits(std::move(registry));

  {  // external update +3    ( adjusted by rate*time bound)
    auto localVal = 0;
    CountersMessage msg;
    msg.counters = Counters(
        {{"resource.1",
          {{"client.1", 10 * toSeconds(timeMeter()) - localVal + 3}}}});
    limiter.applyUpdateResponse(std::move(msg));
  }

  // access weight 7
  EXPECT_TRUE(limiter.access("client.1", "resource.1", 7));
  // reject weight 1
  EXPECT_FALSE(limiter.access("client.1", "resource.1", 1));

  timeMeter() += seconds(1);  // time step

  // check locals
  EXPECT_EQ(limiter.shardCounters(),
            Counters({{"resource.1", {{"client.1", 7}}}}));
  {  // external update +3    ( adjusted by rate*time bound)
    auto localVal = 7;
    CountersMessage msg;
    msg.counters = Counters(
        {{"resource.1",
          {{"client.1", 10 * toSeconds(timeMeter()) - localVal + 3}}}});
    limiter.applyUpdateResponse(std::move(msg));
  }

  // allowed weight 7
  EXPECT_TRUE(limiter.access("client.1", "resource.1", 7));
  // rejected weight 1
  EXPECT_FALSE(limiter.access("client.1", "resource.1", 1));

  // counters check at the end
  EXPECT_EQ(limiter.shardCounters(),
            Counters({{"resource.1", {{"client.1", 14}}}}));
}

TEST(AccessLimiter, ResetLimits) {
  ManualClock timeMeter;
  AccessLimiter limiter(std::ref(timeMeter));
  LimitsRegistry registry(
      {
          {"client.1",
           {{"resource.3", LimitInfo(10, 10, 1)}}}  // specific limit
      },
      1);
  limiter.resetLimits(std::move(registry));

  // access weight 3
  EXPECT_TRUE(limiter.access("client.1", "resource.3", 3));

  // set lower limit
  limiter.resetLimits(
      LimitsRegistry({{"client.1", {{"resource.3", LimitInfo(5, 5, 1)}}}}, 1));

  // access weight 2, expect success
  EXPECT_TRUE(limiter.access("client.1", "resource.3", 2));

  // access weight 1, now expect reject
  EXPECT_FALSE(limiter.access("client.1", "resource.3", 1));

  // set higher limit
  limiter.resetLimits(LimitsRegistry(
      {{"client.1", {{"resource.3", LimitInfo(10, 10, 1)}}}}, 1));

  // access weight 5, now expect success again
  EXPECT_TRUE(limiter.access("client.1", "resource.3", 5));

  // access weight 1, now limit is exceeded
  EXPECT_FALSE(limiter.access("client.1", "resource.3", 1));

  // time tick
  timeMeter() += seconds(1);

  // access weight 10, we're good again
  EXPECT_TRUE(limiter.access("client.1", "resource.3", 10));

  // access weight 1, limit exceeded one more time
  EXPECT_FALSE(limiter.access("client.1", "resource.3", 1));
}

TEST(AccessLimiter, LateLimits) {
  ManualClock timeMeter;
  AccessLimiter limiter(std::ref(timeMeter));

  // No limits configuration at start (all requests allowed)

  // clientA
  EXPECT_TRUE(limiter.access("client.A", "resource.1", 10));
  timeMeter() += seconds(1);
  // time passes nothing changes
  EXPECT_TRUE(limiter.access("client.A", "resource.1", 10));

  // clientB
  EXPECT_TRUE(limiter.access("client.B", "resource.1", 10));

  // Limits config arrived
  limiter.resetLimits(LimitsRegistry(
      {{"client.A", {{"resource.1", LimitInfo(10, 10, 1)}}}}, 1));

  // clientA reject, limit 200 already reached (100+100)
  EXPECT_FALSE(limiter.access("client.A", "resource.1", 1));

  timeMeter() += seconds(1);
  // but time passes and we good again
  EXPECT_TRUE(limiter.access("client.A", "resource.1", 10));
  // until limit is reached
  EXPECT_FALSE(limiter.access("client.A", "resource.1", 1));
}

TEST(AccessLimiter, GarbageCollect) {
  ManualClock timeMeter;
  AccessLimiter limiter(std::ref(timeMeter));
  LimitsRegistry registry(
      {
          {"",
           {{"resource.1",
             LimitInfo(10, 30, 1)}}}  // 'anybody' limit to resource.1
      },
      1);
  limiter.resetLimits(std::move(registry));

  EXPECT_TRUE(limiter.access("client.1", "resource.1", 5));
  EXPECT_TRUE(limiter.access("client.2", "resource.1", 5));
  EXPECT_TRUE(limiter.access("client.3", "resource.1", 15));

  // check counters state
  EXPECT_EQ(limiter.shardCounters(),
            Counters({{"resource.1",
                       {{"client.1", 5}, {"client.2", 5}, {"client.3", 15}}}}));

  timeMeter() += seconds(1);

  EXPECT_TRUE(limiter.access("client.1", "resource.1", 5));
  limiter.garbageCollectCounters();

  EXPECT_EQ(  // client.2 counter thrown into garbage
      limiter.shardCounters(),
      Counters({{"resource.1", {{"client.1", 10}, {"client.3", 15}}}}));

  timeMeter() += seconds(1);

  EXPECT_TRUE(limiter.access("client.1", "resource.1", 5));
  limiter.garbageCollectCounters();

  EXPECT_EQ(  // client.3 counter thrown into garbage
      limiter.shardCounters(), Counters({{"resource.1", {{"client.1", 15}}}}));

  timeMeter() += seconds(1);

  limiter.garbageCollectCounters();

  // no counters left, just empty resource entry
  EXPECT_EQ(limiter.shardCounters(), Counters({{"resource.1", {}}}));
}

TEST(AccessLimiter, CountersMessage) {
  ManualClock timeMeter;
  AccessLimiter limiter(std::ref(timeMeter));
  // Initialize counters with some values.
  EXPECT_TRUE(limiter.access("client.1", "resource.1", 5));
  // We initialize AccessLimiter state with applyUpdateResponse method as it
  // would requested on start.
  auto pluginState = limiter.createUpdateMessage();  // We create update message
                                                     // for ratelimiter proxy.
  // Suppose proxy responded with some lamport.
  auto responseLamport = 42;
  CountersMessage msg;
  msg.lamport = responseLamport;
  limiter.applyUpdateResponse(msg);

  pluginState = limiter.createUpdateMessage();
  EXPECT_EQ(pluginState.counters,
            Counters({{"resource.1", {{"client.1", 5}}}}));
  ASSERT_TRUE(pluginState.lamport);
  EXPECT_EQ(
      pluginState.lamport,
      responseLamport + 1);  // lamport incremented on prepare counters message

  msg.lamport = pluginState.lamport - 10;
  ASSERT_THROW(limiter.applyUpdateResponse(msg),
               maps::rate_limiter2::RuntimeError);

  // Update with correct lamport
  msg.lamport = pluginState.lamport;
  EXPECT_NO_THROW(limiter.applyUpdateResponse(msg));
}

}  // namespace maps::rate_limiter2::agent::tests
