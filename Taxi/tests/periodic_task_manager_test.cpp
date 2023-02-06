
#include <functional>

#include <userver/utest/utest.hpp>
#include <userver/utils/periodic_task.hpp>

#include <userver/engine/sleep.hpp>

#include <utils/periodic_task_manager.hpp>

namespace {

struct MockPeriodicTask {
 public:
  using Callback = std::function<void()>;
  using Settings = utils::PeriodicTask::Settings;

  MockPeriodicTask() : is_running_(false) {}

  ~MockPeriodicTask() { EXPECT_FALSE(is_running_); }

  void Start(std::string name, utils::PeriodicTask::Settings settings,
             Callback /* callback */) {
    ASSERT_FALSE(is_running_);
    name_ = name;
    GetSettingsMap().emplace(name_, settings);
    ++GetCountStarted();
    is_running_ = true;
  }

  void Stop() {
    ASSERT_TRUE(is_running_);
    ++GetCountStopped();
    is_running_ = false;
  }

  void SetSettings(const utils::PeriodicTask::Settings& settings) {
    if (auto it = GetSettingsMap().find(name_); it != GetSettingsMap().end()) {
      it->second = settings;
    } else {
      GetSettingsMap().emplace(name_, settings);
    }
  }

  static size_t& GetCountStarted() {
    static size_t count_started = 0;
    return count_started;
  }

  static size_t& GetCountStopped() {
    static size_t count_stopped = 0;
    return count_stopped;
  }

  static std::unordered_map<std::string, Settings>& GetSettingsMap() {
    static std::unordered_map<std::string, Settings> map;
    return map;
  }

  static void Reset() {
    GetCountStarted() = 0;
    GetCountStopped() = 0;
    GetSettingsMap().clear();
  }

 private:
  bool is_running_;
  std::string name_;
};

using PeriodicTaskManager = utils::impl::PeriodicTaskManager<MockPeriodicTask>;

}  // namespace

UTEST(PeriodicTaskManager, StartStop) {
  MockPeriodicTask::Reset();

  PeriodicTaskManager task_mgr;
  task_mgr.StartWork(
      "task", []() {},
      models::WorkerSettings{3, std::chrono::milliseconds(100)});
  task_mgr.StopWork();

  ASSERT_EQ(3, MockPeriodicTask::GetCountStarted());
  ASSERT_EQ(3, MockPeriodicTask::GetCountStopped());
}

UTEST(PeriodicTaskManager, AddTask) {
  MockPeriodicTask::Reset();

  PeriodicTaskManager task_mgr;
  task_mgr.StartWork(
      "task", []() {},
      models::WorkerSettings{1, std::chrono::milliseconds(100)});

  ASSERT_EQ(1, MockPeriodicTask::GetCountStarted());

  task_mgr.ApplySettings(
      models::WorkerSettings{3, std::chrono::milliseconds(100)});

  ASSERT_EQ(3, MockPeriodicTask::GetCountStarted());

  task_mgr.StopWork();

  ASSERT_EQ(3, MockPeriodicTask::GetCountStopped());
}

UTEST(PeriodicTaskManager, RemoveTask) {
  MockPeriodicTask::Reset();

  PeriodicTaskManager task_mgr;
  task_mgr.StartWork(
      "task", []() {},
      models::WorkerSettings{3, std::chrono::milliseconds(100)});

  ASSERT_EQ(3, MockPeriodicTask::GetCountStarted());
  ASSERT_EQ(0, MockPeriodicTask::GetCountStopped());

  task_mgr.ApplySettings(
      models::WorkerSettings{1, std::chrono::milliseconds(100)});

  ASSERT_EQ(3, MockPeriodicTask::GetCountStarted());
  ASSERT_EQ(2, MockPeriodicTask::GetCountStopped());

  task_mgr.StopWork();

  ASSERT_EQ(3, MockPeriodicTask::GetCountStopped());
}

UTEST(PeriodicTaskManager, ChangeRestartTimeout) {
  MockPeriodicTask::Reset();
  auto& settings_map = MockPeriodicTask::GetSettingsMap();

  PeriodicTaskManager task_mgr;
  task_mgr.StartWork(
      "task", []() {},
      models::WorkerSettings{3, std::chrono::milliseconds(100)});

  for (const auto& settings : settings_map) {
    ASSERT_EQ(std::chrono::milliseconds(100), settings.second.period);
  }

  task_mgr.ApplySettings(
      models::WorkerSettings{3, std::chrono::milliseconds(180)});

  for (const auto& settings : settings_map) {
    ASSERT_EQ(std::chrono::milliseconds(180), settings.second.period);
  }

  task_mgr.StopWork();
}
