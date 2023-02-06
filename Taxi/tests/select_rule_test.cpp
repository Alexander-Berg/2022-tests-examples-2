#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <stq/tasks/driver_fix.hpp>

clients::billing_subventions::DriverFixRule CreateRule(
    const std::string& id, const std::string& start, const std::string& end,
    const std::vector<std::string>& tags) {
  clients::billing_subventions::DriverFixRule rule;

  rule.subvention_rule_id = id;
  rule.start = utils::datetime::Stringtime(start);
  rule.end = utils::datetime::Stringtime(end);
  rule.tags = tags;

  return rule;
}

TEST(SelectRule, Test) {
  const auto& current_rule = CreateRule("origin", "2019-01-01T00:00:00+0000",
                                        "2019-01-02T00:00:00+0000", {});

  const auto now = utils::datetime::Stringtime("2019-01-02T00:00:00+0000");
  utils::datetime::MockNowSet(now);

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        current_rule};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              std::nullopt);
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("new", "2019-01-02T00:00:00+0000",
                   "2019-01-03T00:00:00+0000", {})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              "new");
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("outdated", "2019-01-01T00:00:00+0000",
                   "2019-01-01T01:00:00+0000", {})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              std::nullopt);
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("outdated", "2019-01-01T00:00:00+0000",
                   "2019-01-01T01:00:00+0000", {}),
        CreateRule("real", "2019-01-02T00:00:00+0000",
                   "2019-01-03T01:00:00+0000", {})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              "real");
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("real1", "2019-01-02T00:00:00+0000",
                   "2019-01-03T01:00:00+0000", {}),
        CreateRule("real2", "2019-01-02T00:00:00+0000",
                   "2019-01-04T01:00:00+0000", {})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              "real2");
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("real2", "2019-01-02T00:00:00+0000",
                   "2019-01-04T01:00:00+0000", {}),
        CreateRule("real1", "2019-01-02T00:00:00+0000",
                   "2019-01-03T01:00:00+0000", {})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              "real2");
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("real2", "2019-01-02T00:00:00+0000",
                   "2019-01-04T01:00:00+0000", {}),
        CreateRule("real1", "2019-01-02T00:00:00+0000",
                   "2019-01-03T01:00:00+0000", {})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              "real2");
  }
}

TEST(SelectRule, TestTags) {
  const std::string tag_1 = "tag_1";
  const std::string tag_2 = "tag_2";

  const auto& current_rule = CreateRule("origin", "2019-01-01T00:00:00+0000",
                                        "2019-01-02T00:00:00+0000", {tag_1});

  const auto now = utils::datetime::Stringtime("2019-01-02T00:00:00+0000");
  utils::datetime::MockNowSet(now);

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        current_rule};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              std::nullopt);
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("tagged", "2019-01-02T00:00:00+0000",
                   "2019-01-04T01:00:00+0000", {tag_1})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              "tagged");
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("invalid_tagged", "2019-01-02T00:00:00+0000",
                   "2019-01-04T01:00:00+0000", {tag_2})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              std::nullopt);
  }
}

TEST(SelectRule, TestMultiTags) {
  const std::string tag_1 = "tag_1";
  const std::string tag_2 = "tag_2";
  const std::string tag_3 = "tag_3";

  const auto& current_rule =
      CreateRule("origin", "2019-01-01T00:00:00+0000",
                 "2019-01-02T00:00:00+0000", {tag_1, tag_2});

  const auto now = utils::datetime::Stringtime("2019-01-02T00:00:00+0000");
  utils::datetime::MockNowSet(now);

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        current_rule};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              std::nullopt);
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("tagged", "2019-01-02T00:00:00+0000",
                   "2019-01-04T01:00:00+0000", {tag_1, tag_2})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              "tagged");
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("tagged", "2019-01-02T00:00:00+0000",
                   "2019-01-04T01:00:00+0000", {tag_2, tag_1})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              "tagged");
  }

  {
    std::vector<clients::billing_subventions::DriverFixRule> subventions{
        CreateRule("invalid_tagged", "2019-01-02T00:00:00+0000",
                   "2019-01-04T01:00:00+0000", {tag_2, tag_1, tag_3})};
    ASSERT_EQ(stq_tasks::driver_fix::SelectRule(std::move(subventions),
                                                current_rule, now),
              std::nullopt);
  }
}
