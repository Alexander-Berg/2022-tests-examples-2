#include <userver/utest/utest.hpp>

#include <userver/storages/postgres/cluster.hpp>
#include <userver/storages/postgres/options.hpp>

#include <components/helpers/query_history.hpp>

namespace ch = components::helpers;
namespace pg = storages::postgres;

TEST(QueryHistory, GetHostPreference) {
  using RP = taxi_config::history_host_preference_by_job::RequestPreference;
  using cht = pg::ClusterHostType;

  {
    EXPECT_EQ(ch::impl::GetHostPreference(handlers::Sort::kAsc, {}),
              cht::kSlave);
  }
  {
    RP rp{};
    rp.asc.use_master = true;

    EXPECT_EQ(ch::impl::GetHostPreference(handlers::Sort::kAsc, rp),
              cht::kMaster);
  }

  {
    EXPECT_EQ(ch::impl::GetHostPreference(handlers::Sort::kDesc, {}),
              cht::kSlave);
  }
  {
    RP rp{};
    rp.desc.use_master = true;

    EXPECT_EQ(ch::impl::GetHostPreference(handlers::Sort::kDesc, rp),
              cht::kMaster);
  }
}

TEST(QueryHistory, GetTimeouts) {
  using RT = taxi_config::history_timeouts_by_job::RequestTimeouts;
  using TD = std::chrono::milliseconds;

  {
    EXPECT_EQ(ch::impl::GetTimeouts(handlers::Sort::kAsc, {}),
              pg::CommandControl(TD(0), TD(0)));
  }
  {
    RT rt{};
    rt.asc.execute_timeout_ms = TD(10);
    rt.asc.statement_timeout_ms = TD(11);

    EXPECT_EQ(ch::impl::GetTimeouts(handlers::Sort::kAsc, rt),
              pg::CommandControl(TD(10), TD(11)));
  }

  {
    EXPECT_EQ(ch::impl::GetTimeouts(handlers::Sort::kDesc, {}),
              pg::CommandControl(TD(0), TD(0)));
  }
  {
    RT rt{};
    rt.desc.execute_timeout_ms = TD(10);
    rt.desc.statement_timeout_ms = TD(11);

    EXPECT_EQ(ch::impl::GetTimeouts(handlers::Sort::kDesc, rt),
              pg::CommandControl(TD(10), TD(11)));
  }
}
