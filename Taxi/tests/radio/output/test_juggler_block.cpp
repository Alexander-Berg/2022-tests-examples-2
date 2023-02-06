#include <gtest/gtest.h>

#include <atomic>

#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <models/link.hpp>
#include <notify/notification_center.hpp>
#include <radio/blocks/output/juggler_block.hpp>

namespace hejmdal::radio {

class NotifyJugglerMock : public notify::NotificationCenter {
 public:
  virtual void Post(clients::models::JugglerRawEvent&& event) override {
    events.push_back(std::move(event));
  }

  std::vector<clients::models::JugglerRawEvent> events;
};

TEST(TestJugglerBlock, MainTest) {
  // monday june 8 15:09:01 UTC 2020
  auto now = time::From<time::Milliseconds>(1591628941045);
  ::utils::datetime::MockNowSet(now);

  auto notifications_enabled = std::make_shared<std::atomic<bool>>(true);
  auto nc = std::make_shared<NotifyJugglerMock>();
  auto juggler = blocks::JugglerBlock(
      {nc,
       "host",
       models::JugglerServiceName{"service"},
       {},
       notifications_enabled,
       {}},
      {time::Seconds{60}, time::Seconds{300}, time::Seconds{600}});
  blocks::State state(blocks::State::kWarn, "Description");
  formats::json::ValueBuilder json;
  models::Link link1{"link 1", "http://hello.world/foo=bar;baz/",
                     models::LinkType::kYasmChart};
  json["metric_link_list"].PushBack(link1);
  models::Link link2{"link 2", "http://hello2.world2?foo=bar&baz",
                     models::LinkType::kSolomonAutoGraph};
  json["metric_link_list"].PushBack(link2);
  blocks::Meta meta(json.ExtractValue());

  juggler.StateIn(meta, now, state);
  juggler.StateIn(meta, now + time::Minutes(5), blocks::State::kOk);

  ASSERT_EQ(nc->events.size(), 2u);
  const auto& warn_event = nc->events.front();
  EXPECT_EQ(warn_event.status, clients::models::JugglerRawEventStatus::kWarn);
  EXPECT_EQ(warn_event.host, "host");
  EXPECT_EQ(warn_event.service, "service");
  EXPECT_EQ(
      warn_event.description,
      "~\nDescription\n * link 1: "
      "http://hello.world/foo=bar;baz/?from=1591625341045&to=1591632541045\n"
      " * link 2: "
      "http://"
      "hello2.world2?foo=bar&baz&b=2020-06-08T14%3A09%3A01Z&e=2020-06-08T16%"
      "3A09%3A01Z\n------------------\n~");
  const auto& ok_event = nc->events.back();
  EXPECT_EQ(ok_event.status, clients::models::JugglerRawEventStatus::kOk);
}

TEST(TestJugglerBlock, TestEventFormatNoParams) {
  // monday june 8 15:09:01 UTC 2020
  auto now = time::From<time::Milliseconds>(1591628941045);
  ::utils::datetime::MockNowSet(now);

  auto notifications_enabled = std::make_shared<std::atomic<bool>>(true);
  auto nc = std::make_shared<NotifyJugglerMock>();
  auto juggler = blocks::JugglerBlock(
      {nc,
       "host",
       models::JugglerServiceName{"service"},
       {},
       notifications_enabled,
       std::string(
           "{alert_description}\n{metric_link_list}---\nПроект: "
           "{project_name}\nСервис: {service_name}\nХост: {host_name}")},
      {time::Seconds{60}, time::Seconds{300}, time::Seconds{600}});
  blocks::State state(blocks::State::kWarn, "Description");
  formats::json::ValueBuilder json;
  models::Link link1{"link 1", "http://hello.world/foo=bar;baz/",
                     models::LinkType::kYasmChart};
  json["metric_link_list"].PushBack(link1);
  models::Link link2{"link 2", "http://hello2.world2?foo=bar&baz",
                     models::LinkType::kSolomonAutoGraph};
  json["metric_link_list"].PushBack(link2);
  blocks::Meta meta(json.ExtractValue());

  juggler.StateIn(meta, now, state);
  juggler.StateIn(meta, now + time::Minutes(1), blocks::State::kOk);

  ASSERT_EQ(nc->events.size(), 2u);
  const auto& warn_event = nc->events.front();
  EXPECT_EQ(warn_event.status, clients::models::JugglerRawEventStatus::kWarn);
  EXPECT_EQ(warn_event.host, "host");
  EXPECT_EQ(warn_event.service, "service");
  EXPECT_EQ(
      warn_event.description,
      "~\nDescription\n * link 1: "
      "http://hello.world/foo=bar;baz/?from=1591625341045&to=1591632541045\n"
      " * link 2: "
      "http://"
      "hello2.world2?foo=bar&baz&b=2020-06-08T14%3A09%3A01Z&e=2020-06-08T16%"
      "3A09%3A01Z\n"
      "---\n"
      "Проект: --\n"
      "Сервис: --\n"
      "Хост: --\n"
      "------------------\n~");
  const auto& other_event = nc->events.back();
  EXPECT_EQ(other_event.status, clients::models::JugglerRawEventStatus::kWarn);
}

TEST(TestJugglerBlock, TestEventFormatWithParams) {
  // monday june 8 15:09:01 UTC 2020
  auto now = time::From<time::Milliseconds>(1591628941045);
  ::utils::datetime::MockNowSet(now);

  auto notifications_enabled = std::make_shared<std::atomic<bool>>(true);
  auto nc = std::make_shared<NotifyJugglerMock>();
  auto juggler = blocks::JugglerBlock(
      {nc,
       "host",
       models::JugglerServiceName{"service"},
       {},
       notifications_enabled,
       std::string("{alert_description}\n{metric_link_list}\n---\nПроект: "
                   "{project_name}\nСервис: {service_name}\nХост: {host_name}\n"
                   "Домен: {domain}\nURLs: {domains_list}\n---\n"
                   "{grafana_dashboard_link}")},
      {time::Seconds{60}, time::Seconds{300}, time::Seconds{600}});
  blocks::State state(blocks::State::kWarn, "Description");
  formats::json::ValueBuilder json;
  json["service_name"] = "my-service";
  json["host_name"] = "my-host";
  json["domain"]["name"] = "domain_name";
  json["domain"]["dorblu_object"] = "domain_dorblu_object";
  json["domains_list"].PushBack("first.domain.yandex.net");
  json["domains_list"].PushBack("second.domain.yandex.net");
  json["dorblu_objects_list"].PushBack("first_domain_yandex_net");
  json["dorblu_objects_list"].PushBack("second_domain_yandex_net");
  json["grafana_dashboard_link"] = formats::json::MakeObject(
      "type", "grafana_dashboard", "text", "Grafana", "address",
      "https://grafana.yandex-team.ru/d/123test/my_service");

  blocks::Meta meta(json.ExtractValue());

  juggler.StateIn(meta, now, state);
  juggler.StateIn(meta, now + time::Minutes(1), blocks::State::kOk);

  ASSERT_EQ(nc->events.size(), 2u);
  const auto& warn_event = nc->events.front();
  EXPECT_EQ(warn_event.status, clients::models::JugglerRawEventStatus::kWarn);
  EXPECT_EQ(warn_event.host, "host");
  EXPECT_EQ(warn_event.service, "service");
  EXPECT_EQ(warn_event.description,
            "~\nDescription\n\n"
            "---\n"
            "Проект: --\n"
            "Сервис: my-service\n"
            "Хост: my-host\n"
            "Домен: domain_name\n"
            "URLs: \n"
            "    - first.domain.yandex.net\n"
            "    - second.domain.yandex.net\n"
            "---\n"
            " * Grafana: https://grafana.yandex-team.ru/d/123test/my_service\n"
            "------------------\n~");
  const auto& other_event = nc->events.back();
  EXPECT_EQ(other_event.status, clients::models::JugglerRawEventStatus::kWarn);
}

}  // namespace hejmdal::radio
