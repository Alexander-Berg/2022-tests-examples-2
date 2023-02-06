#include <gtest/gtest.h>

#include "tools/services.hpp"

#include <clients/sticker/sticker_highlevel_client.hpp>
#include <external/resource_tuning.hpp>
#include <models/postgres/digest.hpp>
#include <radio/detail/digests/personalized_resource_usage_digest_constructor.hpp>

#include <set>

namespace hejmdal::radio {

namespace {

static auto now = time::Now();

static models::Incident inc1 = []() {
  models::Incident inc;
  inc.description = "test description";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "host::rtc_cpu_usage";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(5);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "closed";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "stable");
  return inc;
}();

static models::Incident inc2 = []() {
  models::Incident inc;
  inc.description = "test description 2";
  inc.alert_status = radio::blocks::State::kCritical;
  inc.circuit_id = "host2::rtc_cpu_usage";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(3);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "open";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "prestable");
  return inc;
}();

static models::Incident inc3 = []() {
  models::Incident inc;
  inc.description = "test description 3";
  inc.alert_status = radio::blocks::State::kNoData;
  inc.circuit_id = "host2::rtc_memory_usage";
  inc.out_point_id = "high_usage";
  inc.start_time = now - time::Minutes(10);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "open";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "stable");
  return inc;
}();

static models::Incident inc4 = []() {
  models::Incident inc;
  inc.description = "test description 4";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "host3::rtc_memory_usage";
  inc.out_point_id = "high_usage";
  inc.start_time = now - time::Minutes(20);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "closed";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 1, "env", "stable");
  return inc;
}();

static models::Incident testing_inc1 = []() {
  models::Incident inc;
  inc.description = "test description";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "host::rtc_cpu_usage_testing";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(5);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "closed";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "testing");
  return inc;
}();

static models::Incident testing_inc2 = []() {
  models::Incident inc;
  inc.description = "test description 2";
  inc.alert_status = radio::blocks::State::kCritical;
  inc.circuit_id = "host2::rtc_cpu_usage_testing";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(3);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "open";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "testing");
  return inc;
}();

static models::Incident testing_inc3 = []() {
  models::Incident inc;
  inc.description = "test description 3";
  inc.alert_status = radio::blocks::State::kNoData;
  inc.circuit_id = "host2::rtc_memory_usage_testing";
  inc.out_point_id = "high_usage";
  inc.start_time = now - time::Minutes(10);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "open";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "testing");
  return inc;
}();

static models::Incident testing_inc4 = []() {
  models::Incident inc;
  inc.description = "test description 4";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "host3::rtc_memory_usage_testing";
  inc.out_point_id = "high_usage";
  inc.start_time = now - time::Minutes(20);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "closed";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 1, "env", "testing");
  return inc;
}();

static models::Incident testing_inc5 = []() {
  models::Incident inc;
  inc.description = "test description";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "host::rtc_cpu_usage_testing";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(5);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "closed";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 3, "env", "testing");
  return inc;
}();

static models::Incident testing_inc6 = []() {
  models::Incident inc;
  inc.description = "test description 2";
  inc.alert_status = radio::blocks::State::kCritical;
  inc.circuit_id = "host2::rtc_cpu_usage_testing";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(3);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "open";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 3, "env", "testing");
  return inc;
}();

static models::Incident testing_inc7 = []() {
  models::Incident inc;
  inc.description = "test description 3";
  inc.alert_status = radio::blocks::State::kNoData;
  inc.circuit_id = "host2::rtc_memory_usage_testing";
  inc.out_point_id = "high_usage";
  inc.start_time = now - time::Minutes(10);
  inc.end_time = now - time::Minutes(2);
  inc.incident_status = "open";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 3, "env", "testing");
  return inc;
}();

static models::Incident low_usage_inc = []() {
  models::Incident inc;
  inc.description = "test description for cpu low usage";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "direct_link::rtc_cpu_low_usage";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(10);
  inc.end_time = now - time::Minutes(5);
  inc.incident_status = "closed";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "stable");
  return inc;
}();

static models::Incident oom_inc1 = []() {
  models::Incident inc;
  inc.description = "test description for oom";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "host::oom_check";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(10);
  inc.end_time = now - time::Minutes(5);
  inc.incident_status = "closed";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "stable");
  return inc;
}();

static models::Incident oom_inc2 = []() {
  models::Incident inc;
  inc.description = "test description for oom";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "host::oom_check";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(15);
  inc.end_time = now - time::Minutes(5);
  inc.incident_status = "closed";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "stable");
  return inc;
}();

static models::Incident testing_oom_inc1 = []() {
  models::Incident inc;
  inc.description = "test description for oom";
  inc.alert_status = radio::blocks::State::kWarn;
  inc.circuit_id = "host::oom_check_testing";
  inc.out_point_id = "low_usage";
  inc.start_time = now - time::Minutes(15);
  inc.end_time = now - time::Minutes(5);
  inc.incident_status = "closed";
  inc.incident_status = "open";
  inc.meta_data =
      formats::json::MakeObject("test_service_index", 0, "env", "testing");
  return inc;
}();

class ResourceTuningMockThrow : public external::ResourceTuning {
 public:
  models::ChangeResourcesDraft TuneBranchResources(
      models::ServiceId, models::BranchId, Tuner,
      std::optional<std::string>) const override {
    throw std::runtime_error("can't tune");
  }

  void MoveToAppliedDrafts(const models::ChangeResourcesDraft&) const override {
  }
};

static const models::ResourceValueMap kCpu2000 = {
    {models::Resource::kCpu, {models::Resource::kCpu, 2000}}};

struct ResourceTuningMock : public external::ResourceTuning {
  models::BranchResources current_resources = {kCpu2000, kCpu2000};
  models::DraftApproveStatus approve_status =
      models::DraftApproveStatus::kNoDecision;
  models::DraftApplyStatus apply_status = models::DraftApplyStatus::kNotStarted;
  mutable std::vector<models::DraftId> applied_drafts = {};
  mutable std::optional<std::string> draft_description;

 public:
  models::ChangeResourcesDraft TuneBranchResources(
      models::ServiceId, models::BranchId branch_id, Tuner tuner,
      std::optional<std::string> description) const override {
    models::ResourceValueMap curr_res = {
        {models::Resource::kCpu, {models::Resource::kCpu, 2000}}};
    auto changes = tuner(current_resources);
    if (changes.empty()) throw std::runtime_error("changes is empty");
    draft_description = description;
    return models::ChangeResourcesDraft{
        models::DraftId{branch_id.GetUnderlying()},
        branch_id,
        approve_status,
        apply_status,
        0,
        0,
        changes};
  }

  void MoveToAppliedDrafts(
      const models::ChangeResourcesDraft& draft) const override {
    applied_drafts.push_back(draft.id);
  }
};

static ResourceTuningMockThrow kResourceTuningThrow{};
static detail::digests::CutResDraftSettings kDefaultDraftSettings{};
static detail::digests::CutResDraftSettings kDraftEnabledSettings{
    true, true, true, {}, {}};

}  // namespace

TEST(TestPersonalizedResourceUsageDigest, MainTest) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  std::set<models::UserName> subscribers = {
      models::UserName("user1"), models::UserName("user2"),
      models::UserName("user3"), models::UserName("user5")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, kResourceTuningThrow, subscribers, 0.5, 0.5, true,
      false, 25, false, kDefaultDraftSettings, true);
  auto result = ctor.Construct({inc1, inc2, inc3});
  const auto& sticker_digests = result.sticker_digests;
  ASSERT_EQ(sticker_digests.size(), 2u);
  for (const auto& sticker_digest : sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "PRODUCTION:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, EmailLimitTest) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};
  std::set<models::UserName> subscribers = {
      models::UserName("user1"), models::UserName("user2"),
      models::UserName("user3"), models::UserName("user5")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, kResourceTuningThrow, subscribers, 0.5, 0.5, true,
      false, 1, false, kDefaultDraftSettings, true);
  auto sticker_digests = ctor.Construct({inc1, inc2, inc3}).sticker_digests;
  ASSERT_EQ(sticker_digests.size(), 1u);
  for (const auto& sticker_digest : sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "PRODUCTION:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, DuplicateToTestingMailingList) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};
  std::set<models::UserName> subscribers = {
      models::UserName("user1"), models::UserName("user2"),
      models::UserName("user3"), models::UserName("user5")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, kResourceTuningThrow, subscribers, 0.5, 0.5, true,
      false, 1, true, kDefaultDraftSettings, true);
  auto sticker_digests = ctor.Construct({inc1, inc2, inc3}).sticker_digests;
  ASSERT_EQ(sticker_digests.size(), 2u);
  {
    auto digest1 = sticker_digests.front();
    hl_client.Send(digest1);
    EXPECT_EQ(
        buffer->address_,
        "hejmdal-personalized-digest-subscription-testing@yandex-team.ru");
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest - for user: user1");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "PRODUCTION:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
  {
    auto digest2 = sticker_digests.back();
    hl_client.Send(digest2);
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "PRODUCTION:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, OneUserForTwoServices) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, kResourceTuningThrow, subscribers, 0.5, 0.5, true,
      false, 25, false, kDefaultDraftSettings, true);
  auto sticker_digests =
      ctor.Construct({inc1, inc2, inc3, inc4}).sticker_digests;
  ASSERT_EQ(sticker_digests.size(), 1u);
  for (const auto& sticker_digest : sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "PRODUCTION:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, TestProdAndTesting) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, kResourceTuningThrow, subscribers, 0.5, 0.5, true,
      false, 25, false, kDefaultDraftSettings, true);
  auto sticker_digests =
      ctor.Construct({inc1, inc2, inc3, inc4, testing_inc1, testing_inc2,
                      testing_inc3, testing_inc4})
          .sticker_digests;
  ASSERT_EQ(sticker_digests.size(), 1u);
  for (const auto& sticker_digest : sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "PRODUCTION:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, TestDrafts) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  ResourceTuningMock tuning_mock;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false, kDraftEnabledSettings, false);
  auto result =
      ctor.Construct({testing_inc4, testing_inc5, testing_inc6, testing_inc7});
  ASSERT_EQ(result.juggler_notifications.size(), 1u);
  EXPECT_EQ(result.juggler_notifications.front().service,
            "hejmdal-cutres-draft-notify");
  EXPECT_EQ(result.juggler_notifications.front().host, "service_4_stable_host");
  EXPECT_EQ(
      result.juggler_notifications.front().description,
      "~\n"
      "Привет!\n"
      "Сервис **service4** (проект project) в ТЕСТИНГЕ не использует "
      "выделенную квоту.\n"
      "Мы сделали драфт на изменение квоты, вам осталось только ОКнуть его:\n"
      " - https://tariff-editor.taxi.tst.yandex-team.ru/drafts/draft/11\n"
      "Если его проигнорировать, через какое-то время придут админы и ОКнут "
      "его сами.\n"
      "Если квота вам действительно нужна - просто отклоните драфт.\n"
      "~");

  ASSERT_TRUE(tuning_mock.draft_description.has_value());
  EXPECT_EQ(
      tuning_mock.draft_description.value(),
      "Это драфт на изменение ресурсов сервиса **service4** (проект project) в "
      "ТЕСТИНГЕ.\n"
      "Он был создан автоматически, т.к. большую часть времени сервис "
      "использует "
      "менее 10% выделенной ему квоты.\n"
      "Ссылка на бранч: "
      "https://tariff-editor.taxi.yandex-team.ru/services/1/edit/4/branches/"
      "11\n\n"
      " - Для применения изменений нужно аппрувнуть драфт. Затем робот "
      "призовет "
      "вас в связанный тикет и попросит окнуть pull request с "
      "изменением service.yaml (в ближайшее время автоматизируем и этот "
      "шаг).\n\n"
      " - Если квота вам действительно нужна - отклоните драфт с комментарием "
      "почему она вам нужна.\n"
      " - Если драфт проигнорировать, то через какое-то время его аппрувнут "
      "админы.\n\n"
      "Stay OK,\n"
      "Hejmdal");

  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "[NEW DRAFT] Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис:\n"
        "     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service4\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service_4_testing?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        " - Драфт на изменение ресурсов: "
        "https://tariff-editor.taxi.tst.yandex-team.ru/drafts/draft/11\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, TestProdDraftLink) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  ResourceTuningMock tuning_mock;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false, kDraftEnabledSettings, true);
  auto result =
      ctor.Construct({testing_inc4, testing_inc5, testing_inc6, testing_inc7});
  ASSERT_EQ(result.juggler_notifications.size(), 1u);
  EXPECT_EQ(result.juggler_notifications.front().service,
            "hejmdal-cutres-draft-notify");
  EXPECT_EQ(result.juggler_notifications.front().host, "service_4_stable_host");
  EXPECT_EQ(
      result.juggler_notifications.front().description,
      "~\n"
      "Привет!\n"
      "Сервис **service4** (проект project) в ТЕСТИНГЕ не использует "
      "выделенную квоту.\n"
      "Мы сделали драфт на изменение квоты, вам осталось только ОКнуть его:\n"
      " - https://tariff-editor.taxi.yandex-team.ru/drafts/draft/11\n"
      "Если его проигнорировать, через какое-то время придут админы и ОКнут "
      "его сами.\n"
      "Если квота вам действительно нужна - просто отклоните драфт.\n"
      "~");

  ASSERT_TRUE(tuning_mock.draft_description.has_value());
  EXPECT_EQ(
      tuning_mock.draft_description.value(),
      "Это драфт на изменение ресурсов сервиса **service4** (проект project) в "
      "ТЕСТИНГЕ.\n"
      "Он был создан автоматически, т.к. большую часть времени сервис "
      "использует "
      "менее 10% выделенной ему квоты.\n"
      "Ссылка на бранч: "
      "https://tariff-editor.taxi.yandex-team.ru/services/1/edit/4/branches/"
      "11\n\n"
      " - Для применения изменений нужно аппрувнуть драфт. Затем робот "
      "призовет "
      "вас в связанный тикет и попросит окнуть pull request с "
      "изменением service.yaml (в ближайшее время автоматизируем и этот "
      "шаг).\n\n"
      " - Если квота вам действительно нужна - отклоните драфт с комментарием "
      "почему она вам нужна.\n"
      " - Если драфт проигнорировать, то через какое-то время его аппрувнут "
      "админы.\n\n"
      "Stay OK,\n"
      "Hejmdal");

  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "[NEW DRAFT] Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис:\n"
        "     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service4\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service_4_testing?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        " - Драфт на изменение ресурсов: "
        "https://tariff-editor.taxi.yandex-team.ru/drafts/draft/11\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, TestDraftRejected) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};
  ResourceTuningMock tuning_mock;
  tuning_mock.approve_status = models::DraftApproveStatus::kRejected;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false, kDraftEnabledSettings, true);
  auto result =
      ctor.Construct({testing_inc1, testing_inc2, testing_inc3, testing_inc4});
  EXPECT_TRUE(result.juggler_notifications.empty());
  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
  EXPECT_EQ(tuning_mock.applied_drafts.size(), 0u);
}

TEST(TestPersonalizedResourceUsageDigest, TestDraftApplied) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};
  ResourceTuningMock tuning_mock;
  tuning_mock.approve_status = models::DraftApproveStatus::kApproved;
  tuning_mock.apply_status = models::DraftApplyStatus::kSucceeded;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false, kDraftEnabledSettings, true);
  auto result =
      ctor.Construct({testing_inc1, testing_inc2, testing_inc3, testing_inc4});
  const auto& sticker_digests = result.sticker_digests;
  EXPECT_TRUE(result.juggler_notifications.empty());

  ASSERT_EQ(sticker_digests.size(), 1u);
  for (const auto& sticker_digest : sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
  EXPECT_EQ(tuning_mock.applied_drafts.size(), 1u);
}

TEST(TestPersonalizedResourceUsageDigest, TestDraftFailed) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};
  ResourceTuningMock tuning_mock;
  tuning_mock.approve_status = models::DraftApproveStatus::kApproved;
  tuning_mock.apply_status = models::DraftApplyStatus::kFailed;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false, kDraftEnabledSettings, true);
  auto result =
      ctor.Construct({testing_inc1, testing_inc2, testing_inc3, testing_inc4});
  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
  EXPECT_EQ(tuning_mock.applied_drafts.size(), 0u);
}

TEST(TestPersonalizedResourceUsageDigest, TestChangeInProgress) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};
  ResourceTuningMock tuning_mock;
  tuning_mock.current_resources.remote_values.at(models::Resource::kCpu) =
      models::ResourceValue{models::Resource::kCpu, 1000};

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false, kDraftEnabledSettings, true);
  auto result =
      ctor.Construct({testing_inc1, testing_inc2, testing_inc3, testing_inc4});
  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
  EXPECT_EQ(tuning_mock.applied_drafts.size(), 0u);
}

TEST(TestPersonalizedResourceUsageDigest, TestDraftSettingsEmailOnly) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  ResourceTuningMock tuning_mock;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false, detail::digests::CutResDraftSettings{true, false, true, {}, {}},
      false);
  auto result =
      ctor.Construct({testing_inc4, testing_inc5, testing_inc6, testing_inc7});
  EXPECT_EQ(result.juggler_notifications.size(), 0u);

  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "[NEW DRAFT] Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис:\n"
        "     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service4\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service_4_testing?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        " - Драфт на изменение ресурсов: "
        "https://tariff-editor.taxi.tst.yandex-team.ru/drafts/draft/11\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, TestDraftSettingsJugglerOnly) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  ResourceTuningMock tuning_mock;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false, detail::digests::CutResDraftSettings{true, true, false, {}, {}},
      false);
  auto result =
      ctor.Construct({testing_inc4, testing_inc5, testing_inc6, testing_inc7});
  ASSERT_EQ(result.juggler_notifications.size(), 1u);
  EXPECT_EQ(result.juggler_notifications.front().service,
            "hejmdal-cutres-draft-notify");
  EXPECT_EQ(result.juggler_notifications.front().host, "service_4_stable_host");
  EXPECT_EQ(
      result.juggler_notifications.front().description,
      "~\n"
      "Привет!\n"
      "Сервис **service4** (проект project) в ТЕСТИНГЕ не использует "
      "выделенную квоту.\n"
      "Мы сделали драфт на изменение квоты, вам осталось только ОКнуть его:\n"
      " - https://tariff-editor.taxi.tst.yandex-team.ru/drafts/draft/11\n"
      "Если его проигнорировать, через какое-то время придут админы и ОКнут "
      "его сами.\n"
      "Если квота вам действительно нужна - просто отклоните драфт.\n"
      "~");

  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис:\n"
        "     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service4\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service_4_testing?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, TestDraftSettingsServiceWhitelist) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  ResourceTuningMock tuning_mock;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false,
      detail::digests::CutResDraftSettings{
          true, true, true, {models::ServiceId{2}}, {}},
      true);
  auto result =
      ctor.Construct({testing_inc4, testing_inc5, testing_inc6, testing_inc7});
  ASSERT_EQ(result.juggler_notifications.size(), 0u);

  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис:\n"
        "     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service4\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service_4_testing?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, TestDraftSettingsServiceWhitelist2) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  ResourceTuningMock tuning_mock;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false,
      detail::digests::CutResDraftSettings{
          true, true, true, {models::ServiceId{4}}, {}},
      false);
  auto result =
      ctor.Construct({testing_inc4, testing_inc5, testing_inc6, testing_inc7});
  ASSERT_EQ(result.juggler_notifications.size(), 1u);
  EXPECT_EQ(result.juggler_notifications.front().service,
            "hejmdal-cutres-draft-notify");
  EXPECT_EQ(result.juggler_notifications.front().host, "service_4_stable_host");
  EXPECT_EQ(
      result.juggler_notifications.front().description,
      "~\n"
      "Привет!\n"
      "Сервис **service4** (проект project) в ТЕСТИНГЕ не использует "
      "выделенную квоту.\n"
      "Мы сделали драфт на изменение квоты, вам осталось только ОКнуть его:\n"
      " - https://tariff-editor.taxi.tst.yandex-team.ru/drafts/draft/11\n"
      "Если его проигнорировать, через какое-то время придут админы и ОКнут "
      "его сами.\n"
      "Если квота вам действительно нужна - просто отклоните драфт.\n"
      "~");

  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "[NEW DRAFT] Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис:\n"
        "     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service4\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service_4_testing?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        " - Драфт на изменение ресурсов: "
        "https://tariff-editor.taxi.tst.yandex-team.ru/drafts/draft/11\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, TestDraftSettingsServiceBlacklist) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  ResourceTuningMock tuning_mock;

  std::set<models::UserName> subscribers = {models::UserName("user1")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, tuning_mock, subscribers, 0.5, 0.5, true, false, 25,
      false,
      detail::digests::CutResDraftSettings{
          true, true, true, {}, {models::ServiceId{4}}},
      true);
  auto result =
      ctor.Construct({testing_inc4, testing_inc5, testing_inc6, testing_inc7});
  ASSERT_EQ(result.juggler_notifications.size(), 0u);

  ASSERT_EQ(result.sticker_digests.size(), 1u);
  for (const auto& sticker_digest : result.sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    EXPECT_EQ(buffer->address_, "user1@yandex-team.ru");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис:\n"
        "     service2\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service2_testing_branch_direct_link?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: OK\n"
        " - RAM: overload: ~ 30%\n"
        "-----------------------------------------------\n"
        " - Проект: project\n"
        " - Сервис:\n     service4\n"
        "       * Системный дашборд -- "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_service_4_testing?from=" +
        std::to_string(time::To<time::Milliseconds>(digest.last_broadcast)) +
        "&to=" +
        std::to_string(time::To<time::Milliseconds>(
            digest.last_broadcast + time::Hours{digest.period_hours})) +
        "\n"
        " - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, CpuLowUsageTest) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  std::set<models::UserName> subscribers = {
      models::UserName("user1"), models::UserName("user2"),
      models::UserName("user3"), models::UserName("user5")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, kResourceTuningThrow, subscribers, 0.5, 0.5, true,
      false, 25, false, kDefaultDraftSettings, true);
  auto result = ctor.Construct({inc1, inc2, low_usage_inc});
  const auto& sticker_digests = result.sticker_digests;
  ASSERT_EQ(sticker_digests.size(), 2u);
  for (const auto& sticker_digest : sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "PRODUCTION:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n"
        " - CPU: underload: ~ 13%\n"
        " - RAM: OK\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

TEST(TestPersonalizedResourceUsageDigest, OomTest) {
  auto buffer = std::make_shared<Buffer>();
  auto hl_client = clients::StickerHighLevelClient(buffer, "Source <s@s.s>");

  models::postgres::Digest digest{1,
                                  "test digest",
                                  "a@a.a",
                                  now - time::Hours(1),
                                  1,
                                  "personalized_resource_usage",
                                  "Digest description",
                                  {},
                                  std::nullopt,
                                  {}};

  std::set<models::UserName> subscribers = {
      models::UserName("user1"), models::UserName("user2"),
      models::UserName("user3"), models::UserName("user5")};
  detail::digests::PersonalizedResourceUsageDigestConstructor ctor(
      digest, &GetService, kResourceTuningThrow, subscribers, 0.5, 0.5, true,
      false, 25, false, kDefaultDraftSettings, true);
  auto result =
      ctor.Construct({inc1, inc2, inc3, oom_inc1, oom_inc2, testing_oom_inc1});
  const auto& sticker_digests = result.sticker_digests;
  ASSERT_EQ(sticker_digests.size(), 2u);
  for (const auto& sticker_digest : sticker_digests) {
    hl_client.Send(sticker_digest);
    EXPECT_EQ(buffer->email_.from, "Source <s@s.s>");
    EXPECT_EQ(buffer->email_.subject, "Digest: test digest");
    std::string body(
        "\nDigest description\n\n"
        "===============================================\n\n"
        "PRODUCTION:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: underload: ~ 5%\n"
        " - RAM: overload: ~ 13%, OOM: 2 times\n"
        "-----------------------------------------------\n\n"
        "TESTING:\n\n"
        " - Проект: project\n"
        " - Сервис: service1\n - CPU: OK\n"
        " - RAM: OOM: 1 times\n"
        "-----------------------------------------------\n\n"
        "___________________\nStay OK,\nHejmdal\n");
    EXPECT_EQ(buffer->email_.body, body);
  }
}

}  // namespace hejmdal::radio
