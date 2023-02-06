#include <gmock/gmock.h>
#include <mission_progress_notification.pb.h>
#include <experiments3/cashback_tasks_description.hpp>
#include <modules/mission_progress/common.hpp>
#include <modules/mission_progress/mission_completions.hpp>
#include <modules/mission_progress/mission_progress.hpp>
#include <modules/stats/stats.hpp>
#include <taxi_config/variables/CASHBACK_LEVELS_STAGES_DESCRIPTION.hpp>
#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

namespace mc = plus::mc::core::v1;
using namespace cashback_levels::mission_progress;
using namespace cashback_levels::stage;

mc::MissionProgressNotification GetNotification(
    mc::MissionStatus mission_status,
    mc::NotificationStatus notification_status,
    mc::UserMission::ProgressCase user_mission_progress_case,
    int64_t mission_puid, std::string mission_external_id,
    int64_t cyclic_progress = 5, int version = 0,
    mc::Customer customer = mc::Customer::CUSTOMER_LEVELS) {
  mc::MissionProgressNotification notification{};
  notification.set_status(notification_status);
  notification.mutable_mission()->set_puid(mission_puid);
  notification.mutable_mission()->set_external_id(mission_external_id);
  notification.mutable_mission()->set_status(mission_status);
  notification.mutable_mission()->set_version(version);
  notification.mutable_mission()->set_customer(customer);

  switch (user_mission_progress_case) {
    // This sets oneof field to concrete value.
    case mc::UserMission::ProgressCase::kCounterProgress: {
      notification.mutable_mission()->mutable_counter_progress();
      break;
    }
    case mc::UserMission::ProgressCase::kCyclicProgress: {
      notification.mutable_mission()
          ->mutable_cyclic_progress()
          ->set_current_completed_iteration(cyclic_progress);
      notification.mutable_mission()
          ->mutable_cyclic_progress()
          ->set_target_completed_iteration(10);

      break;
    }
    case mc::UserMission::ProgressCase::kTransactionProgress: {
      break;
    }
    case mc::UserMission::ProgressCase::PROGRESS_NOT_SET: {
      break;
    }
  }

  return notification;
}

std::vector<mc::NotificationStatus> kIgnoredNotificationStatuses{
    mc::NotificationStatus::NOTIFICATION_STATUS_DELETED,
    mc::NotificationStatus::NOTIFICATION_STATUS_INVALID,
};

std::vector<mc::MissionStatus> kIgnoredMissionStatuses{
    mc::MissionStatus::MISSION_STATUS_EXPIRED,
    mc::MissionStatus::MISSION_STATUS_FAILED,
    mc::MissionStatus::MISSION_STATUS_NOT_ACCEPTED,
    mc::MissionStatus::MISSION_STATUS_INVALID,
};

std::vector<mc::MissionStatus> kOkMissionStatuses{
    mc::MissionStatus::MISSION_STATUS_IN_PROGRESS,
    mc::MissionStatus::MISSION_STATUS_COMPLETED,
    mc::MissionStatus::MISSION_STATUS_ACHIEVED,
};

std::vector<mc::UserMission::ProgressCase> kProgressCases{
    mc::UserMission::ProgressCase::kCounterProgress,
    mc::UserMission::ProgressCase::kCyclicProgress,
};

using TimePoint = std::chrono::system_clock::time_point;
const std::string kDumpFilenameDateFormat = "%Y-%m-%dT%H-%M-%S";
const TimePoint kSampleTimePoint1 = ::utils::datetime::Stringtime(
    "2020-08-25T12-00-00", "UTC", kDumpFilenameDateFormat);

dynamic_config::StorageMock CreateConfig(const std::string& val) {
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::CASHBACK_LEVELS_STAGES_DESCRIPTION,
        formats::json::FromString(val)}});
}

dynamic_config::StorageMock CreateDefaultConfig() {
  return CreateConfig(R"({
    "stage1": {
      "start_time": "2020-08-20T12:00:00+0000",
      "end_time": "2020-08-26T12:00:00+0000",
      "stage_id": "stage1",
      "next_stage_id": "stage2"
    }
  })");
}

namespace ctd = experiments3::cashback_tasks_description;
auto json_value = formats::json::FromString(
    R"({
  "button": {
    "icon_tag": "icon_tag",
    "title": "Поехать",
    "url": "url"
  },
  "complete_limit": "whatever",
  "description": {
    "footer": "Баллы придут в течение суток",
    "text": "5 econom orders"
  },
  "id": "kek",
  "level": "1",
  "parameters": {
    "target": "whatever"
  },
  "service": "eda",
  "stage_id": "stage1",
  "status": "whatever",
  "target": "whatever",
  "template_id": "whatever",
  "title": "whatever",
  "type": "transaction"
})");
ctd::TaskDescription task_descr =
    ctd::Parse(json_value, formats::parse::To<ctd::TaskDescription>{});
cashback_levels::exp3::TasksDescriptionUmap tasks_description{
    {"kek", task_descr}};

TEST(TestGetMissionProgress,
     TestGetMissionProgressIgnoredNotificationStatuses) {
  for (auto notification_status : kIgnoredNotificationStatuses) {
    for (auto progress_case : kProgressCases) {
      for (auto mission_status : kOkMissionStatuses) {
        std::vector<mc::MissionProgressNotification> notifications{
            GetNotification(mission_status, notification_status, progress_case,
                            123, "kek")};
        RemoveIgnoredNotifications(notifications);
        ASSERT_TRUE(notifications.size() == 0);
      }
    }
  }
}

TEST(TestGetMissionProgress, TestGetMissionProgressIgnoredMissionStatuses) {
  for (auto progress_case : kProgressCases) {
    for (auto mission_status : kIgnoredMissionStatuses) {
      std::vector<mc::MissionProgressNotification> notifications{
          GetNotification(mission_status,
                          mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED,
                          progress_case, 123, "kek")};
      RemoveIgnoredNotifications(notifications);
      ASSERT_TRUE(notifications.size() == 0);
    }
  }
}

TEST(TestGetMissionProgress, TestMissionsWithWrongCustomer) {
  std::vector<mc::MissionProgressNotification> notifications{
      GetNotification(mc::MissionStatus::MISSION_STATUS_COMPLETED,
                      mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED,
                      mc::UserMission::ProgressCase::kCounterProgress, 123,
                      "kek", 5, 0, mc::Customer::CUSTOMER_CITY),
      GetNotification(mc::MissionStatus::MISSION_STATUS_COMPLETED,
                      mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED,
                      mc::UserMission::ProgressCase::kCounterProgress, 123,
                      "kek", 5, 0, mc::Customer::CUSTOMER_INVALID)};
  RemoveIgnoredNotifications(notifications);
  ASSERT_TRUE(notifications.size() == 0);
}

TEST(TestGetMissionProgress, TestGetMissionProgressCounterMissionOne) {
  std::vector<mc::MissionProgressNotification> notifications{GetNotification(
      mc::MissionStatus::MISSION_STATUS_COMPLETED,
      mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED,
      mc::UserMission::ProgressCase::kCounterProgress, 123, "kek")};
  RemoveIgnoredNotifications(notifications);
  ASSERT_TRUE(notifications.size() == 1);

  utils::datetime::MockNowSet(kSampleTimePoint1);
  auto config = CreateDefaultConfig();
  cashback_levels::Statistics stats{};
  MissionProgressContext ctx{nullptr, nullptr, nullptr, config.GetSnapshot(),
                             stats};
  MissionProgressProcessing progress_processing{std::move(ctx)};
  auto key =
      progress_processing.GetMissionKey(notifications[0], tasks_description);
  ASSERT_EQ(key->yandex_uid, "123");
  ASSERT_EQ(key->stage_id, "stage1");
  ASSERT_EQ(key->task_description_id, "kek");

  auto progress = GetMissionProgress(notifications[0]);
  ASSERT_TRUE(progress);
  ASSERT_EQ(progress->completions, 1);
}

TEST(TestGetMissionProgress, TestGetMissionProgressCounterMissionZero) {
  std::vector<mc::MissionProgressNotification> notifications{GetNotification(
      mc::MissionStatus::MISSION_STATUS_IN_PROGRESS,
      mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED,
      mc::UserMission::ProgressCase::kCounterProgress, 123, "kek")};
  RemoveIgnoredNotifications(notifications);
  ASSERT_TRUE(notifications.size() == 1);

  utils::datetime::MockNowSet(kSampleTimePoint1);
  auto config = CreateDefaultConfig();
  cashback_levels::Statistics stats{};
  MissionProgressContext ctx{nullptr, nullptr, nullptr, config.GetSnapshot(),
                             stats};
  MissionProgressProcessing progress_processing{std::move(ctx)};
  auto key =
      progress_processing.GetMissionKey(notifications[0], tasks_description);
  ASSERT_TRUE(key);
  ASSERT_EQ(key->yandex_uid, "123");
  ASSERT_EQ(key->stage_id, "stage1");
  ASSERT_EQ(key->task_description_id, "kek");

  auto progress = GetMissionProgress(notifications[0]);
  ASSERT_TRUE(progress);
  ASSERT_EQ(progress->completions, 0);
}

TEST(TestGetMissionProgress, TestGetMissionProgressCyclicMissionOkStatuses) {
  std::vector<mc::MissionStatus> zero_mission_statuses{
      mc::MissionStatus::MISSION_STATUS_IN_PROGRESS,
      mc::MissionStatus::MISSION_STATUS_COMPLETED,
      mc::MissionStatus::MISSION_STATUS_ACHIEVED,
  };

  for (const auto& mission_status : zero_mission_statuses) {
    std::vector<mc::MissionProgressNotification> notifications{GetNotification(
        mission_status, mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED,
        mc::UserMission::ProgressCase::kCyclicProgress, 123, "kek")};

    utils::datetime::MockNowSet(kSampleTimePoint1);
    auto config = CreateDefaultConfig();
    cashback_levels::Statistics stats{};
    MissionProgressContext ctx{nullptr, nullptr, nullptr, config.GetSnapshot(),
                               stats};
    MissionProgressProcessing progress_processing{std::move(ctx)};
    auto key =
        progress_processing.GetMissionKey(notifications[0], tasks_description);
    ASSERT_TRUE(key);
    ASSERT_EQ(key->yandex_uid, "123");
    ASSERT_EQ(key->stage_id, "stage1");
    ASSERT_EQ(key->task_description_id, "kek");

    auto progress = GetMissionProgress(notifications[0]);
    ASSERT_TRUE(progress);
    ASSERT_EQ(progress->completions, 5);
  }
}

TEST(TestGetMissionProgress, TestGetMissionProgressCyclicMissionCompleted) {
  std::vector<mc::MissionProgressNotification> notifications{GetNotification(
      mc::MissionStatus::MISSION_STATUS_COMPLETED,
      mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED,
      mc::UserMission::ProgressCase::kCyclicProgress, 123, "kek")};

  utils::datetime::MockNowSet(kSampleTimePoint1);
  auto config = CreateDefaultConfig();
  cashback_levels::Statistics stats{};
  MissionProgressContext ctx{nullptr, nullptr, nullptr, config.GetSnapshot(),
                             stats};
  MissionProgressProcessing progress_processing{std::move(ctx)};
  auto key =
      progress_processing.GetMissionKey(notifications[0], tasks_description);
  ASSERT_TRUE(key);
  ASSERT_EQ(key->yandex_uid, "123");
  ASSERT_EQ(key->stage_id, "stage1");
  ASSERT_EQ(key->task_description_id, "kek");

  auto progress = GetMissionProgress(notifications[0]);
  ASSERT_TRUE(progress);
  ASSERT_EQ(progress->completions, 5);
}

TEST(TestGetMissionProgress, TestGetMissionProgressCyclicMissionInProgress) {
  std::vector<mc::MissionProgressNotification> notifications{GetNotification(
      mc::MissionStatus::MISSION_STATUS_IN_PROGRESS,
      mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED,
      mc::UserMission::ProgressCase::kCyclicProgress, 123, "kek")};

  utils::datetime::MockNowSet(kSampleTimePoint1);
  auto config = CreateDefaultConfig();
  cashback_levels::Statistics stats{};
  MissionProgressContext ctx{nullptr, nullptr, nullptr, config.GetSnapshot(),
                             stats};
  MissionProgressProcessing progress_processing{std::move(ctx)};
  auto key =
      progress_processing.GetMissionKey(notifications[0], tasks_description);
  ASSERT_TRUE(key);
  ASSERT_EQ(key->yandex_uid, "123");
  ASSERT_EQ(key->stage_id, "stage1");
  ASSERT_EQ(key->task_description_id, "kek");

  auto progress = GetMissionProgress(notifications[0]);
  ASSERT_TRUE(progress);
  ASSERT_EQ(progress->completions, 5);
}
