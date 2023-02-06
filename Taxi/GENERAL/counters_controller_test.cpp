#include "counters_controller.hpp"

#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

void MockTime(const int seconds) {
  utils::datetime::MockNowSet(
      std::chrono::system_clock::time_point{std::chrono::seconds{seconds}});
}

}  // namespace

UTEST(CountersController, AdvanceCounters) {
  MockTime(1);

  rate_limiter::CountersController controller;
  const int64_t limits_version = 1;
  models::Limits limits{{{"path1", {{"client1", {100, 50}}}}}, limits_version};
  controller.UpdateLimits(limits);

  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1", {{{"path1", {{"client1", 10}}}}, 1, limits_version}),
      models::SyncMessage({{{"path1", {{"client1", 0}}}}, 1, limits_version}));

  controller.AdvanceCounters();

  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1", {{{"path1", {{"client1", 10}}}}, 2, limits_version}),
      models::SyncMessage({{{"path1", {{"client1", 90}}}}, 2, limits_version}));

  MockTime(10);
  controller.AdvanceCounters();

  EXPECT_EQ(controller.SyncDownstream(
                "shard1", {{{"path1", {{"client1", 10}}}}, 3, limits_version}),
            models::SyncMessage(
                {{{"path1", {{"client1", 990}}}}, 3, limits_version}));

  controller.SyncUpstream({{{"path1", {{"client1", 20}}}}, 3, limits_version});
  EXPECT_EQ(controller.SyncDownstream(
                "shard1", {{{"path1", {{"client1", 10}}}}, 3, limits_version}),
            models::SyncMessage(
                {{{"path1", {{"client1", 1010}}}}, 3, limits_version}));

  controller.UpdateLimits(limits, limits);
  EXPECT_EQ(controller.SyncDownstream(
                "shard1", {{{"path1", {{"client1", 10}}}}, 3, limits_version}),
            models::SyncMessage(
                {{{"path1", {{"client1", 990}}}}, 3, limits_version}));
}

UTEST(CountersController, UpdateLimits) {
  MockTime(1);

  rate_limiter::CountersController controller;
  int64_t limits_version = 0;

  int64_t shard1_lamport = 1;
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1",
          {{{"path1", {{"client1", 10}}}}, shard1_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 0}}}}, shard1_lamport, limits_version}));

  controller.AdvanceCounters();  // update other total

  shard1_lamport += 1;
  EXPECT_EQ(controller.SyncDownstream("shard1", {{{"path1", {{"client1", 10}}}},
                                                 shard1_lamport,
                                                 limits_version}),
            models::SyncMessage({{{"path1", {{"client1", 9999990}}}},
                                 shard1_lamport,
                                 limits_version}));

  controller.UpdateLimits(
      {{{"path1", {{"client1", {100, 0}}}}}, ++limits_version});

  shard1_lamport += 1;
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1",
          {{{"path1", {{"client1", 10}}}}, shard1_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 90}}}}, shard1_lamport, limits_version}));

  controller.UpdateLimits(
      {{{"path1", {{"client1", {1000, 0}}}}}, ++limits_version});

  shard1_lamport += 1;
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1",
          {{{"path1", {{"client1", 10}}}}, shard1_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 990}}}}, shard1_lamport, limits_version}));
}

UTEST(CountersController, Lamport) {
  MockTime(1);

  rate_limiter::CountersController controller;
  const int64_t limits_version = 1;
  controller.UpdateLimits(
      {{{"path1", {{"client1", {100, 50}}}}}, limits_version});

  // shard1 sync with correct lamport
  int64_t shard1_lamport = 10;
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1",
          {{{"path1", {{"client1", 10}}}}, shard1_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 0}}}}, shard1_lamport, limits_version}));
  // shard2 sync with correct lamport
  int64_t shard2_lamport = 5;
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard2",
          {{{"path1", {{"client1", 20}}}}, shard2_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 10}}}}, shard2_lamport, limits_version}));

  MockTime(2);
  // shard1 sync with incorrect lamport (not incremented)
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1",
          {{{"path1", {{"client1", 15}}}}, shard1_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 15}}}}, shard1_lamport, limits_version}));
  // shard2 sync with incorrect lamport (not incremented)
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard2",
          {{{"path1", {{"client1", 23}}}}, shard2_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 7}}}}, shard2_lamport, limits_version}));

  MockTime(3);
  // shard1 sync with correct lamport
  shard1_lamport += 1;
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1",
          {{{"path1", {{"client1", 16}}}}, shard1_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 20}}}}, shard1_lamport, limits_version}));
  // shard2 sync with correct lamport
  shard2_lamport += 3;
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard2",
          {{{"path1", {{"client1", 24}}}}, shard2_lamport, limits_version}),
      models::SyncMessage(
          {{{"path1", {{"client1", 16}}}}, shard2_lamport, limits_version}));
}

UTEST(CountersController, Sync) {
  MockTime(1);

  rate_limiter::CountersController controller;
  const int64_t limits_version = 1;
  controller.UpdateLimits(
      {{{"path1", {{"client1", {100, 0}}}}, {"path2", {{"client2", {10, 0}}}}},
       limits_version});

  // initial sync with upstream
  int64_t proxy_lamport = 1;
  controller.SyncUpstream({{{"path1", {{"client1", 150}, {"client2", 50}}},
                            {"path2", {{"client2", 200}}}},
                           proxy_lamport,
                           limits_version});

  // shard 1 sync (+check incorrect limits version)
  int64_t shard1_lamport = 1;
  EXPECT_EQ(
      controller.SyncDownstream(
          "shard1",
          {{{"path1", {{"client1", 10}}}}, shard1_lamport, limits_version + 5}),
      models::SyncMessage({{{"path1", {{"client1", 150}, {"client2", 50}}}},
                           shard1_lamport,
                           limits_version}));
  // shard 2 sync
  int64_t shard2_lamport = 1;
  EXPECT_EQ(
      controller.SyncDownstream("shard2", {{{"path1", {{"client1", 20}}},
                                            {"path2", {{"client2", 20}}}},
                                           shard2_lamport,
                                           limits_version}),
      models::SyncMessage({{{"path1", {{"client1", 160}, {"client2", 50}}},
                            {"path2", {{"client2", 200}}}},
                           shard2_lamport,
                           limits_version}));
  // sync with upstream
  proxy_lamport += 1;
  EXPECT_EQ(controller.GetUpstreamSyncMessage(),
            models::SyncMessage(
                {{{"path1", {{"client1", 30}}}, {"path2", {{"client2", 20}}}},
                 proxy_lamport,
                 limits_version}));
  controller.SyncUpstream(
      {{{"path1", {{"client1", 100}}}, {"path2", {{"client2", 50}}}},
       proxy_lamport,
       limits_version});

  MockTime(2);
  // sync shard 2
  shard2_lamport += 1;
  EXPECT_EQ(
      controller.SyncDownstream("shard2", {{{"path1", {{"client1", 30}}},
                                            {"path2", {{"client2", 30}}}},
                                           shard2_lamport,
                                           limits_version}),
      models::SyncMessage({{{"path1", {{"client1", 260}, {"client2", 50}}},
                            {"path2", {{"client2", 250}}}},
                           shard2_lamport,
                           limits_version}));
  // sync shard 1
  shard1_lamport += 1;
  EXPECT_EQ(
      controller.SyncDownstream("shard1", {{{"path1", {{"client1", 20}}},
                                            {"path2", {{"client1", 20}}}},
                                           shard1_lamport,
                                           limits_version}),
      models::SyncMessage({{{"path1", {{"client1", 280}, {"client2", 50}}},
                            {"path2", {{"client1", 0}, {"client2", 280}}}},
                           shard1_lamport,
                           limits_version}));
}

UTEST(CountersController, CollectGarbage) {
  MockTime(1);

  rate_limiter::CountersController controller;
  controller.UpdateLimits({{{"path1", {{"client1", {100, 0}}}}}, 1});

  EXPECT_EQ(controller.SyncDownstream("shard1",
                                      {{{"path1", {{"client1", 10}}}}, 1, 1}),
            (models::SyncMessage{{{"path1", {{"client1", 0}}}}, 1, 1}));

  MockTime(2);

  EXPECT_EQ(controller.SyncDownstream("shard2",
                                      {{{"path1", {{"client1", 20}}}}, 1, 1}),
            (models::SyncMessage{{{"path1", {{"client1", 10}}}}, 1, 1}));

  EXPECT_EQ(controller.GetUpstreamSyncMessage(),
            (models::SyncMessage{{{"path1", {{"client1", 30}}}}, 1, 1}));

  // Should reset shard1 data as outdated
  controller.CollectGarbage(utils::datetime::SteadyNow());

  EXPECT_EQ(controller.SyncDownstream("shard1",
                                      {{{"path1", {{"client1", 10}}}}, 2, 1}),
            (models::SyncMessage{{{"path1", {{"client1", 30}}}}, 2, 1}));

  MockTime(3);

  EXPECT_EQ(controller.SyncDownstream("shard2",
                                      {{{"path1", {{"client1", 30}}}}, 2, 1}),
            (models::SyncMessage{{{"path1", {{"client1", 20}}}}, 2, 1}));
  EXPECT_EQ(controller.GetUpstreamSyncMessage(),
            (models::SyncMessage{{{"path1", {{"client1", 50}}}}, 2, 1}));

  MockTime(4);

  // Should collect all counters
  controller.CollectGarbage(utils::datetime::SteadyNow());
  EXPECT_EQ(controller.GetUpstreamSyncMessage(),
            (models::SyncMessage{{}, 3, 1}));
}
