#include <gtest/gtest.h>
#include "gmock/gmock.h"

#include "flow/agent_task_scheduler.hpp"

namespace dorblu {

class MockQueue : public dorblu::flow::QueueAgentBase {
 public:
  void ScheduleTask(std::chrono::system_clock::time_point t,
                    const std::string& name) override {
    tasks_.push_back(std::make_pair(t, name));
  }
  const std::vector<
      std::pair<std::chrono::system_clock::time_point, std::string>>&
  GetTasks() const {
    return tasks_;
  }
  void Clear() { tasks_.clear(); }

 private:
  std::vector<std::pair<std::chrono::system_clock::time_point, std::string>>
      tasks_;
};

class MockServiceProvider : public dorblu::flow::ServiceProviderBase {
 public:
  std::vector<std::string> GetServiceList(bool) override { return services_; }

  void SetServices(const std::vector<std::string>& services) {
    services_ = services;
  }

 private:
  std::vector<std::string> services_;
};

TEST(TestAgentTaskScheduler, TestEmpty) {
  MockQueue queue;
  MockServiceProvider service_provider;
  dorblu::flow::AgentTaskScheduler scheduler(&queue, &service_provider);
  std::chrono::system_clock::time_point time_point(std::chrono::hours(10234));
  scheduler.Run(time_point, false);
  ASSERT_TRUE(queue.GetTasks().empty());
}

TEST(TestAgentTaskScheduler, TestSimple) {
  MockQueue queue;
  MockServiceProvider service_provider;
  dorblu::flow::AgentTaskScheduler scheduler(&queue, &service_provider);
  service_provider.SetServices({"service_a", "service_b", "service_c"});
  std::chrono::system_clock::time_point time_point(std::chrono::hours(10234));
  scheduler.Run(time_point, false);
  ASSERT_THAT(queue.GetTasks(),
              ::testing::ElementsAre(std::make_pair(time_point, "service_a"),
                                     std::make_pair(time_point, "service_b"),
                                     std::make_pair(time_point, "service_c")));
}

TEST(TestAgentTaskScheduler, TestSameTimeCycle) {
  MockQueue queue;
  MockServiceProvider service_provider;
  dorblu::flow::AgentTaskScheduler scheduler(&queue, &service_provider);
  service_provider.SetServices({"service_a", "service_b", "service_c"});
  std::chrono::system_clock::time_point time_point1(std::chrono::hours(10234) +
                                                    std::chrono::seconds(1));
  std::chrono::system_clock::time_point time_point2(std::chrono::hours(10234) +
                                                    std::chrono::seconds(2));
  std::chrono::system_clock::time_point time_point_x(std::chrono::hours(10234) +
                                                     std::chrono::seconds(60));
  scheduler.Run(time_point1, false);
  ASSERT_THAT(queue.GetTasks(), ::testing::ElementsAre(
                                    std::make_pair(time_point_x, "service_a"),
                                    std::make_pair(time_point_x, "service_b"),
                                    std::make_pair(time_point_x, "service_c")));
  queue.Clear();
  scheduler.Run(time_point2, false);
  ASSERT_THAT(queue.GetTasks(), ::testing::ElementsAre());
}

TEST(TestAgentTaskScheduler, TestTwoCycles) {
  MockQueue queue;
  MockServiceProvider service_provider;
  dorblu::flow::AgentTaskScheduler scheduler(&queue, &service_provider);
  service_provider.SetServices({"service_a", "service_b", "service_c"});
  std::chrono::system_clock::time_point time_point1(std::chrono::hours(10234));
  std::chrono::system_clock::time_point time_point2(std::chrono::hours(10234) +
                                                    std::chrono::seconds(1));
  std::chrono::system_clock::time_point time_point2x(std::chrono::hours(10234) +
                                                     std::chrono::seconds(60));
  scheduler.Run(time_point1, false);
  ASSERT_THAT(queue.GetTasks(),
              ::testing::ElementsAre(std::make_pair(time_point1, "service_a"),
                                     std::make_pair(time_point1, "service_b"),
                                     std::make_pair(time_point1, "service_c")));
  queue.Clear();
  scheduler.Run(time_point2, false);
  ASSERT_THAT(queue.GetTasks(), ::testing::ElementsAre(
                                    std::make_pair(time_point2x, "service_a"),
                                    std::make_pair(time_point2x, "service_b"),
                                    std::make_pair(time_point2x, "service_c")));
}

}  // namespace dorblu
