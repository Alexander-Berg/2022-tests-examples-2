#include <gtest/gtest.h>
#include <iostream>

#include <agent/lib/access_limiter.h>

namespace std {
std::ostream& operator<<(std::ostream& os,
                         taxi::rate_limiter2::CheckStatus result) {
  switch (result) {
    case taxi::rate_limiter2::CheckStatus::kAllow:
      return os << "Allow";
    case taxi::rate_limiter2::CheckStatus::kReject:
      return os << "Reject";
    case taxi::rate_limiter2::CheckStatus::kUpdateQuota:
      return os << "UpdateQuota";
    case taxi::rate_limiter2::CheckStatus::kForbidden:
      return os << "Forbidden";
  }
  throw std::runtime_error("Unknown result");
}
}  // namespace std

namespace taxi::rate_limiter2::agent::tests {

using std::chrono::system_clock;

namespace {

class ManualClock {
  system_clock::time_point t_;

 public:
  ManualClock(system_clock::time_point t = system_clock::now()) : t_(t) {}

  system_clock::time_point operator()() const { return t_; }
  system_clock::time_point& operator()() { return t_; }
};

}  // anonymous namespace

TEST(AccessLimiter, AllowAndReject) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client1", "path1", 10});
  limiter.SetQuota({"client1", "path2", 20});
  limiter.SetQuota({"client2", "path3", 30});
  limiter.SetQuota({"client2", "path4", 40});

  for (auto i = 0; i < 10; ++i) {
    EXPECT_EQ(limiter.Access("client1", "path1", 1).status,
              CheckStatus::kAllow);
  }
  EXPECT_EQ(limiter.Access("client1", "path1", 1).status,
            CheckStatus::kUpdateQuota);

  // no quota from the rate-limiter-proxy
  limiter.SetQuota({"client1", "path1", 0});

  EXPECT_EQ(limiter.Access("client1", "path1", 1).status, CheckStatus::kReject);

  clock() += std::chrono::milliseconds(500);
  // still rejecting
  EXPECT_EQ(limiter.Access("client1", "path1", 1).status, CheckStatus::kReject);
  clock() += std::chrono::milliseconds(500);
  // ask to update quotas again
  EXPECT_EQ(limiter.Access("client1", "path1", 1).status,
            CheckStatus::kUpdateQuota);

  limiter.SetQuota({"client1", "path1", 10});
  for (auto i = 0; i < 10; ++i) {
    EXPECT_EQ(limiter.Access("client1", "path1", 1).status,
              CheckStatus::kAllow);
  }
  EXPECT_EQ(limiter.Access("client1", "path1", 1).status,
            CheckStatus::kUpdateQuota);
}

TEST(AccessLimiter, RegexpResources) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client1", R"(/test/[\w]+)", 10, true});
  limiter.SetQuota(
      {"client1", R"(/test/specific/handler7)", -2});  // no limit, allow

  for (auto i = 0; i < 10; ++i) {
    EXPECT_EQ(limiter.Access("client1", "/test/handler" + std::to_string(i), 1)
                  .status,
              CheckStatus::kAllow);
  }
  EXPECT_EQ(limiter.Access("client1", "/test/handler_empty", 1).status,
            CheckStatus::kUpdateQuota);

  // no quota from the rate-limiter-proxy
  limiter.SetQuota({"client1", R"(/test/[\w]+)", 0});

  EXPECT_EQ(limiter.Access("client1", "/test/handler_reject", 1).status,
            CheckStatus::kReject);

  clock() += std::chrono::milliseconds(500);
  // still rejecting
  EXPECT_EQ(limiter.Access("client1", "/test/handler_reject2", 1).status,
            CheckStatus::kReject);
  clock() += std::chrono::milliseconds(500);
  // ask to update quotas again
  EXPECT_EQ(limiter.Access("client1", "/test/handler_update", 1).status,
            CheckStatus::kUpdateQuota);

  EXPECT_EQ(limiter.Access("client1", "/test/specific/handler7", 1).status,
            CheckStatus::kAllow);
}

TEST(AccessLimiter, UpdateIfNoQuota) {
  AccessLimiter limiter;

  limiter.SetQuota({"client1", "path1", 1});

  for (auto i = 0; i < 3; ++i) {
    EXPECT_EQ(limiter.Access("client3", "path1", 1).status,
              CheckStatus::kUpdateQuota);
  }
}

TEST(AccessLimiter, DefaultClientAndPath) {
  AccessLimiter limiter;

  limiter.SetQuota({"client", "path[1-3]", 1, true});
  limiter.SetQuota({"client", "", 0});
  limiter.SetQuota({"", "path[7-9]", -1, true});
  limiter.SetQuota({"", "", 0});

  // quota for client and path1 exists
  EXPECT_EQ(limiter.Access("client", "path1", 1).status, CheckStatus::kAllow);
  // no quota for client + path4, use default path with quota 0
  EXPECT_EQ(limiter.Access("client", "path4", 1).status, CheckStatus::kReject);
  // no client2 quota, use default client
  EXPECT_EQ(limiter.Access("client2", "path7", 1).status,
            CheckStatus::kForbidden);
  // default client + default path is not supported
  EXPECT_EQ(limiter.Access("client3", "path4", 1).status,
            CheckStatus::kUpdateQuota);
}

TEST(AccessLimiter, DifferentStatesAndFallbackQuota) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client", "path", 10});
  EXPECT_EQ(limiter.Access("client", "path", 1).status, CheckStatus::kAllow);
  // make access for 'client' to 'path' forbidden
  limiter.SetQuota({"client", "path", -1});
  EXPECT_EQ(limiter.Access("client", "path", 1).status,
            CheckStatus::kForbidden);

  // forbidden_until has not passed yet
  clock() += std::chrono::milliseconds(4500);
  EXPECT_EQ(limiter.Access("client", "path", 1).status,
            CheckStatus::kForbidden);
  clock() += std::chrono::milliseconds(500);
  EXPECT_EQ(limiter.Access("client", "path", 1).status,
            CheckStatus::kUpdateQuota);
  // simulate rate-limiter-proxy is down
  limiter.SetFallbackQuota("client", "path");
  // forbidden state is preserved
  EXPECT_EQ(limiter.Access("client", "path", 1).status,
            CheckStatus::kForbidden);

  // reject requests
  limiter.SetQuota({"client", "path", 0});
  EXPECT_EQ(limiter.Access("client", "path", 1).status, CheckStatus::kReject);

  clock() += std::chrono::milliseconds(850);
  EXPECT_EQ(limiter.Access("client", "path", 1).status,
            CheckStatus::kUpdateQuota);
  // simulate rate-limiter-proxy is down
  limiter.SetFallbackQuota("client", "path");
  // reject state is preserved
  EXPECT_EQ(limiter.Access("client", "path", 1).status, CheckStatus::kReject);

  // set no limit
  limiter.SetQuota({"client", "path", -2});
  // limiter is still rejecting
  EXPECT_EQ(limiter.Access("client", "path", 1).status, CheckStatus::kReject);
  // wait until this rule becomes obsolete
  clock() += std::chrono::milliseconds(850);
  EXPECT_EQ(limiter.Access("client", "path", 1).status,
            CheckStatus::kUpdateQuota);

  clock() += std::chrono::milliseconds(3650);
  for (auto i = 0; i < 20; i++) {
    EXPECT_EQ(limiter.Access("client", "path", 1).status, CheckStatus::kAllow);
  }
  // 5 seconds passed, no limit rule is obsolete now
  clock() += std::chrono::milliseconds(500);
  EXPECT_EQ(limiter.Access("client", "path", 1).status,
            CheckStatus::kUpdateQuota);
  // simulate rate-limiter-proxy is down
  limiter.SetFallbackQuota("client", "path");
  // no limit state is preserved
  EXPECT_EQ(limiter.Access("client", "path", 1).status, CheckStatus::kAllow);
}

TEST(AccessLimiter, HandlerName) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client", "path", 10});
  auto result = limiter.Access("client", "path", 1);
  EXPECT_EQ(result.status, CheckStatus::kAllow);
  EXPECT_EQ(result.handler_name, std::nullopt);

  limiter.SetQuota({"client", "path", 10, false, "my_handler_name"});
  result = limiter.Access("client", "path", 1);
  EXPECT_EQ(result.status, CheckStatus::kAllow);
  EXPECT_EQ(result.handler_name.value(), "my_handler_name");
}

TEST(AccessLimiter, SetFallbackQuotaForDefaultRule) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetFallbackQuota("client", "resource1");
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kAllow);

  // now set real quota value for resource1
  limiter.SetQuota({"", "resource\\d", 0, true});
  // fallback quota value should be ignored
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kReject);
}

TEST(AccessLimiter, RuleHasChanged) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client", "resource1", 1});
  // spend whole quota
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kAllow);
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kUpdateQuota);

  // now mock case when old rule client:resource1 has been
  // removed from rate-limiter-proxy. /quota request for client:resource1
  // returns new rule
  limiter.SetQuota({"client", "resource\\d+", 10, true});
  // old rule shall be ignored now
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kAllow);
}

TEST(AccessLimiter, DefaultRuleHasChanged) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"", "resource1", 1});
  // spend whole quota
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kAllow);
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kUpdateQuota);

  limiter.SetQuota({"", "resource\\d+", 10, true});
  // old rule shall be ignored now
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kAllow);
}

TEST(AccessLimiter, RuleHasChangedToDefaultOne) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client", "resource1", 1});
  // spend whole quota
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kAllow);
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kUpdateQuota);

  // now mock case when old rule client:resource1 has been
  // removed from rate-limiter-proxy
  limiter.SetQuota({"", "resource\\d+", 10, true});
  // old rule shall be ignored now
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kAllow);
}

TEST(AccessLimiter, DefaultRulesPriority) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"", "resource1", 100});
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kAllow);

  limiter.SetQuota({"client", "", 0});
  EXPECT_EQ(limiter.Access("client", "resource1", 1).status,
            CheckStatus::kReject);
}

TEST(AccessLimiter, AbsentRuleAndRegexPath) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client1", "resource1", -2});
  EXPECT_EQ(limiter.Access("client1", "resource1", 1).status,
            CheckStatus::kAllow);

  limiter.SetQuota({"", "resource\\d+", 0, true});
  EXPECT_EQ(limiter.Access("client1", "resource1", 1).status,
            CheckStatus::kReject);
}

TEST(AccessLimiter, AllTypeRulesPriority) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client", "resource", -2});
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kAllow);

  limiter.SetQuota({"", "resource", -1});
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kForbidden);

  limiter.SetQuota({"client", "", 0});
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kReject);

  limiter.SetQuota({"client", "res\\w+", 1, true});
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kAllow);

  limiter.SetQuota({"client", "resource", 5});
  for (auto i = 0; i < 5; i++) {
    EXPECT_EQ(limiter.Access("client", "resource", 1).status,
              CheckStatus::kAllow);
  }
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kUpdateQuota);
  // simulate that all the rules have been removed and now there is no limit
  limiter.SetQuota({"client", "resource", -2});

  // simple rule client:resource is removed, now regexp rule is requesting
  // update
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kUpdateQuota);
  limiter.SetQuota({"client", "resource", -2});
  // regexp rule is removed, we in reject state by client:"" rule
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kReject);

  clock() += std::chrono::milliseconds(850);
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kUpdateQuota);
  limiter.SetQuota({"client", "resource", -2});
  // client:"" rule is removed, we're in forbidden rule again
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kForbidden);
  clock() += std::chrono::milliseconds(4150);
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kUpdateQuota);
  limiter.SetQuota({"client", "resource", -2});
  // "":resource rule is removed, we're in no limit rule and allow requests
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kAllow);
}

TEST(AccessLimiter, OutdatedQuotas) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  // the least priority quota
  limiter.SetQuota({"client", "resource", -2});

  limiter.SetQuota({"", "resource", -1});
  limiter.SetQuota({"client", "", -1});
  limiter.SetQuota({"client", "res\\w+", -1, true});
  limiter.SetQuota({"client", "resource", -1});
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kForbidden);

  // make all quotas outdated
  clock() += std::chrono::seconds(60);

  limiter.SetQuota({"client", "resource", -2});
  EXPECT_EQ(limiter.Access("client", "resource", 1).status,
            CheckStatus::kAllow);
}

TEST(AccessLimiter, FallbackQuotaStacking) {
  ManualClock clock;
  AccessLimiter limiter(std::ref(clock));

  limiter.SetQuota({"client", "/v1/cached-value/test", 2});
  EXPECT_EQ(limiter.Access("client", "/v1/cached-value/test", 1).status,
            CheckStatus::kAllow);
  EXPECT_EQ(limiter.Access("client", "/v1/cached-value/test", 1).status,
            CheckStatus::kAllow);
  EXPECT_EQ(limiter.Access("client", "/v1/cached-value/test", 1).status,
            CheckStatus::kUpdateQuota);

  // last assigned == 1, but we don't stack fallback quota so total quota == 1
  limiter.SetFallbackQuota("client", "/v1/cached-value/test");
  limiter.SetFallbackQuota("client", "/v1/cached-value/test");

  EXPECT_EQ(limiter.Access("client", "/v1/cached-value/test", 1).status,
            CheckStatus::kAllow);
  EXPECT_EQ(limiter.Access("client", "/v1/cached-value/test", 1).status,
            CheckStatus::kAllow);
  EXPECT_EQ(limiter.Access("client", "/v1/cached-value/test", 1).status,
            CheckStatus::kUpdateQuota);
}

}  // namespace taxi::rate_limiter2::agent::tests
