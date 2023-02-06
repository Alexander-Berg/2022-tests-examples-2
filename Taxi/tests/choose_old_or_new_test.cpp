#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>

#include <api_over_data/revise_helpers.hpp>

namespace {
const std::string kConsumer = "test_consumer";
const std::string kConsumerSpecialization = "test_specialization";
const std::string kLogHint = "log_hint";

struct TestModel {
  enum OldOrNewWay { kOldWay, kNewWay };
  OldOrNewWay way;
  bool operator==(const TestModel&) const { return true; }
};

std::ostream& operator<<(std::ostream& out, const TestModel&) { return out; }

config::DocsMap DocsMapForTest(const std::string& workmode) {
  config::DocsMap docs_map = config::DocsMapForTest();
  mongo::BSONObjBuilder test_specialization;
  test_specialization.append(kConsumerSpecialization, workmode);
  mongo::BSONObjBuilder test_consumer;
  test_consumer.append(kConsumer, test_specialization.obj());
  docs_map.Override("API_OVER_DATA_WORK_MODE", test_consumer.obj());
  return docs_map;
}

}  // namespace

TEST(ReviseHelpers, TestOldWay) {
  auto docs_map = DocsMapForTest("oldway");
  config::Config config(docs_map);

  auto old_way_visited = 0;
  auto old_way = [&old_way_visited]() {
    old_way_visited++;
    return TestModel{TestModel::kOldWay};
  };

  auto new_way_visited = 0;
  auto new_way = [&new_way_visited]() {
    new_way_visited++;
    return TestModel{TestModel::kNewWay};
  };

  TestModel result;
  auto choose = [&result, &config, &old_way, &new_way]() {
    result = api_over_data::ChooseOldOrNew<TestModel>(
        config, boost::none, kConsumer, kConsumerSpecialization, kLogHint,
        old_way, new_way, LogExtra{});
  };
  ASSERT_NO_THROW(choose());
  ASSERT_EQ(TestModel::kOldWay, result.way);
  ASSERT_EQ(1, old_way_visited);
  ASSERT_EQ(0, new_way_visited);
}

TEST(ReviseHelpers, TestNewWay) {
  auto docs_map = DocsMapForTest("newway");
  config::Config config(docs_map);

  auto old_way_visited = 0;
  auto old_way = [&old_way_visited]() {
    old_way_visited++;
    return TestModel{TestModel::kOldWay};
  };

  auto new_way_visited = 0;
  auto new_way = [&new_way_visited]() {
    new_way_visited++;
    return TestModel{TestModel::kNewWay};
  };

  TestModel result;
  auto choose = [&result, &config, &old_way, &new_way]() {
    result = api_over_data::ChooseOldOrNew<TestModel>(
        config, boost::none, kConsumer, kConsumerSpecialization, kLogHint,
        old_way, new_way, LogExtra{});
  };
  ASSERT_NO_THROW(choose());
  ASSERT_EQ(TestModel::kNewWay, result.way);
  ASSERT_EQ(0, old_way_visited);
  ASSERT_EQ(1, new_way_visited);
}

TEST(ReviseHelpers, TestDryRun) {
  auto docs_map = DocsMapForTest("dryrun");
  config::Config config(docs_map);

  auto old_way_visited = 0;
  auto old_way = [&old_way_visited]() {
    old_way_visited++;
    return TestModel{TestModel::kOldWay};
  };

  auto new_way_visited = 0;
  auto new_way = [&new_way_visited]() {
    new_way_visited++;
    return TestModel{TestModel::kNewWay};
  };

  TestModel result;
  auto choose = [&result, &config, &old_way, &new_way]() {
    result = api_over_data::ChooseOldOrNew<TestModel>(
        config, boost::none, kConsumer, kConsumerSpecialization, kLogHint,
        old_way, new_way, LogExtra{});
  };
  ASSERT_NO_THROW(choose());
  ASSERT_EQ(TestModel::kOldWay, result.way);
  ASSERT_EQ(1, old_way_visited);
  ASSERT_EQ(1, new_way_visited);
}

TEST(ReviseHelpers, TestTryOut) {
  auto docs_map = DocsMapForTest("tryout");
  config::Config config(docs_map);

  auto old_way_visited = 0;
  auto old_way = [&old_way_visited]() {
    old_way_visited++;
    return TestModel{TestModel::kOldWay};
  };

  auto new_way_visited = 0;
  auto new_way = [&new_way_visited]() {
    new_way_visited++;
    return TestModel{TestModel::kNewWay};
  };

  TestModel result;
  auto choose = [&result, &config, &old_way, &new_way]() {
    result = api_over_data::ChooseOldOrNew<TestModel>(
        config, boost::none, kConsumer, kConsumerSpecialization, kLogHint,
        old_way, new_way, LogExtra{});
  };
  ASSERT_NO_THROW(choose());
  ASSERT_EQ(TestModel::kNewWay, result.way);
  ASSERT_EQ(1, old_way_visited);
  ASSERT_EQ(1, new_way_visited);
}

TEST(ReviseHelpers, TestExtraCriterionNewWayTrue) {
  auto docs_map = DocsMapForTest("newway");
  config::Config config(docs_map);

  auto old_way_visited = 0;
  auto old_way = [&old_way_visited]() {
    old_way_visited++;
    return TestModel{TestModel::kOldWay};
  };

  auto new_way_visited = 0;
  auto new_way = [&new_way_visited]() {
    new_way_visited++;
    return TestModel{TestModel::kNewWay};
  };

  TestModel result;
  auto choose = [&result, &config, &old_way, &new_way]() {
    result = api_over_data::ChooseOldOrNew<TestModel>(
        config, boost::none, kConsumer, kConsumerSpecialization, kLogHint,
        old_way, new_way, LogExtra{}, [](api_over_data::work_mode::Type) {
          return api_over_data::work_mode::Type::kNewWay;
        });
  };
  ASSERT_NO_THROW(choose());
  ASSERT_EQ(TestModel::kNewWay, result.way);
  ASSERT_EQ(0, old_way_visited);
  ASSERT_EQ(1, new_way_visited);
}

TEST(ReviseHelpers, TestExtraCriterionNewWayFalse) {
  auto docs_map = DocsMapForTest("newway");
  config::Config config(docs_map);

  auto old_way_visited = 0;
  auto old_way = [&old_way_visited]() {
    old_way_visited++;
    return TestModel{TestModel::kOldWay};
  };

  auto new_way_visited = 0;
  auto new_way = [&new_way_visited]() {
    new_way_visited++;
    return TestModel{TestModel::kNewWay};
  };

  TestModel result;
  auto choose = [&result, &config, &old_way, &new_way]() {
    result = api_over_data::ChooseOldOrNew<TestModel>(
        config, boost::none, kConsumer, kConsumerSpecialization, kLogHint,
        old_way, new_way, LogExtra{}, [](api_over_data::work_mode::Type) {
          return api_over_data::work_mode::Type::kOldWay;
        });
  };
  ASSERT_NO_THROW(choose());
  ASSERT_EQ(TestModel::kOldWay, result.way);
  ASSERT_EQ(1, old_way_visited);
  ASSERT_EQ(0, new_way_visited);
}

TEST(ReviseHelpers, TestExtraCriterionTryOutTrue) {
  auto docs_map = DocsMapForTest("tryout");
  config::Config config(docs_map);

  auto old_way_visited = 0;
  auto old_way = [&old_way_visited]() {
    old_way_visited++;
    return TestModel{TestModel::kOldWay};
  };

  auto new_way_visited = 0;
  auto new_way = [&new_way_visited]() {
    new_way_visited++;
    return TestModel{TestModel::kNewWay};
  };

  TestModel result;
  auto choose = [&result, &config, &old_way, &new_way]() {
    result = api_over_data::ChooseOldOrNew<TestModel>(
        config, boost::none, kConsumer, kConsumerSpecialization, kLogHint,
        old_way, new_way, LogExtra{}, [](api_over_data::work_mode::Type) {
          return api_over_data::work_mode::Type::kTryOut;
        });
  };
  ASSERT_NO_THROW(choose());
  ASSERT_EQ(TestModel::kNewWay, result.way);
  ASSERT_EQ(1, old_way_visited);
  ASSERT_EQ(1, new_way_visited);
}

TEST(ReviseHelpers, TestExtraCriterionTryOutFalse) {
  auto docs_map = DocsMapForTest("tryout");
  config::Config config(docs_map);

  auto old_way_visited = 0;
  auto old_way = [&old_way_visited]() {
    old_way_visited++;
    return TestModel{TestModel::kOldWay};
  };

  auto new_way_visited = 0;
  auto new_way = [&new_way_visited]() {
    new_way_visited++;
    return TestModel{TestModel::kNewWay};
  };

  TestModel result;
  auto choose = [&result, &config, &old_way, &new_way]() {
    result = api_over_data::ChooseOldOrNew<TestModel>(
        config, boost::none, kConsumer, kConsumerSpecialization, kLogHint,
        old_way, new_way, LogExtra{}, [](api_over_data::work_mode::Type) {
          return api_over_data::work_mode::Type::kDryRun;
        });
  };
  ASSERT_NO_THROW(choose());
  ASSERT_EQ(TestModel::kOldWay, result.way);
  ASSERT_EQ(1, old_way_visited);
  ASSERT_EQ(1, new_way_visited);
}
