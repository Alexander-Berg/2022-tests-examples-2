#include <fstream>
#include <functional>

#include <boost/filesystem.hpp>

#include <testing/source_path.hpp>

#include <clients/shuttle-control/client_mock_base.hpp>
#include <core/context/clients/clients_impl.hpp>
#include <endpoints/full/builders/input_builder.hpp>
#include <endpoints/full/plugins/shuttle_order_flow/plugin.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

const std::string kShortcutOfferId = "52de011a-801c-4d09-b079-1d00c3e3785a";
const std::string kLastSelectedOfferId = "52de011b-801d-4d09-b079-1d00c3e3785a";
const int kSelectedPassengers = 2;

const boost::filesystem::path kTestFilePath(utils::CurrentSourcePath(
    "src/tests/endpoints/full/plugins/shuttle_order_flow"));
const std::string kTestDataDir = kTestFilePath.string() + "/static";

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  std::ifstream f(filename);
  if (!f.is_open()) {
    throw std::runtime_error("Couldn't open file");
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

formats::json::Value GetShuttleInRoutestatsExp() {
  return LoadJsonFromFile(kTestDataDir + "/shuttle_in_routestats.json");
}

formats::json::Value GetShuttleOrderFlowSettingsExp(bool enable_v2_offer) {
  const auto json_name = enable_v2_offer
                             ? "/shuttle_order_flow_settings_offer_v2.json"
                             : "/shuttle_order_flow_settings.json";
  return LoadJsonFromFile(kTestDataDir + json_name);
}

routestats::core::Configs3 MakeConfigs(bool enable_v2_offer) {
  experiments3::models::ExperimentResult res{
      "shuttle_order_flow_settings",
      GetShuttleOrderFlowSettingsExp(enable_v2_offer),
      {}};
  std::unordered_map<std::string, experiments3::models::ExperimentResult>
      mapped_data{{"shuttle_order_flow_settings", res}};
  return routestats::core::Configs3{{mapped_data}};
}

routestats::core::Experiments MakeExperiments() {
  experiments3::models::ExperimentResult res{
      "shuttle_order_flow_settings", GetShuttleInRoutestatsExp(), {}};
  std::unordered_map<std::string, experiments3::models::ExperimentResult>
      mapped_data{{"shuttle_in_routestats", res}};
  return routestats::core::Experiments{mapped_data};
}

}  // namespace
namespace clients::shuttle_control {

namespace {

using Request = internal_shuttle_control_v1_match_shuttles::post::Request;
using Response = internal_shuttle_control_v1_match_shuttles::post::Response;

using Handler = std::function<Response(const Request&, const CommandControl&)>;

class ShuttleControlClient : public clients::shuttle_control::ClientMockBase {
 public:
  ShuttleControlClient(Handler handler) : handler_(std::move(handler)) {}

  Response InternalShuttleControlV1MatchShuttles(
      const Request& req, const CommandControl& cc) const override {
    return handler_(req, cc);
  }

 private:
  Handler handler_;
};

}  // namespace
}  // namespace clients::shuttle_control

namespace routestats::full::shuttle_order_flow {

namespace {

routestats::full::ContextData MakeContext(
    const std::optional<std::string>& context_filename = std::nullopt,
    bool enable_v2_offer = false) {
  auto context = routestats::test::full::GetDefaultContext();
  context.user.auth_context.locale = "ru";
  context.experiments = {MakeExperiments(), MakeConfigs(enable_v2_offer)};
  auto& request = context.input.original_request;

  const auto point_a =
      ::geometry::Position{36.0 * ::geometry::lat, 55.0 * ::geometry::lon};
  const auto point_b =
      ::geometry::Position{36.2 * ::geometry::lat, 55.2 * ::geometry::lon};

  request.route = std::vector<::geometry::Position>{point_a, point_b};
  request.is_lightweight = false;
  if (context_filename) {
    request.summary_context.emplace();
    request.summary_context->by_classes.emplace();
    request.summary_context->by_classes->push_back(
        LoadJsonFromFile(*context_filename)
            .As<handlers::ClassSummaryContext>());
  }

  const auto& input = context.input;
  context.input = routestats::full::BuildRoutestatsInput(
      request, input.tariff_requirements, input.supported_options);

  return context;
}

void CheckRequestShortcut(const clients::shuttle_control::Request& req) {
  const auto& body = req.body;
  const auto& prev_match = body.previous_match;
  ASSERT_TRUE(prev_match);
  ASSERT_EQ(prev_match->offer_id, kShortcutOfferId);
}

void CheckRequestClientContext(const clients::shuttle_control::Request& req) {
  const auto& body = req.body;
  const auto& prev_match = body.previous_match;
  ASSERT_TRUE(prev_match);
  ASSERT_EQ(prev_match->offer_id, kLastSelectedOfferId);
  ASSERT_TRUE(body.passengers_count);
  ASSERT_EQ(*body.passengers_count, kSelectedPassengers);
}

}  // namespace

TEST(TestShuttleOrderFlowPlugin, ShortcutGoodCase) {
  RunInCoro([]() {
    auto context = MakeContext(kTestDataDir + "/only_backend_context.json");

    clients::shuttle_control::ShuttleControlClient client(
        [](const clients::shuttle_control::Request& req,
           const clients::shuttle_control::CommandControl&)
            -> clients::shuttle_control::Response {
          CheckRequestShortcut(req);
          auto resp = LoadJsonFromFile(kTestDataDir + "/v1_match_response.json")
                          .As<clients::shuttle_control::Response>();
          return resp;
        });
    context.clients.shuttle_control = routestats::core::MakeClient(
        static_cast<clients::shuttle_control::Client&>(std::ref(client)));

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    plugins::top_level::ShuttleOrderFlowPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "shuttle";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    extensions.at("shuttle")->Apply("shuttle", level);
    ASSERT_TRUE(level.is_hidden);
    ASSERT_FALSE(level.is_hidden.value());
    ASSERT_FALSE(level.tariff_unavailable);

    const auto level_ptr = plugin.OnServiceLevelRendering(level, plugin_ctx);

    handlers::ServiceLevel handlers_level;
    routestats::plugins::common::ResultWrapper<handlers::ServiceLevel> result(
        handlers_level);
    level_ptr->SerializeInPlace(result);

    ASSERT_TRUE(handlers_level.shuttle_extra);

    const auto& extra = *handlers_level.shuttle_extra;
    ASSERT_EQ(extra.offers.size(), 1);

    const auto& offer = extra.offers.front();
    const auto& v1_offer = std::get<::handlers::ShuttleOfferV1>(offer);

    ASSERT_EQ(v1_offer.shuttle_id, "shortcut_shuttle");
    ASSERT_EQ(v1_offer.route_id, "gkZxnYQ73QGqrKyz");
    ASSERT_EQ(v1_offer.pickup_stop_id, "shortcut_pickup_stop");
    ASSERT_EQ(v1_offer.dropoff_stop_id, "shortcut_dropoff_stop");
    ASSERT_EQ(v1_offer.offer_id, kShortcutOfferId);

    auto promo_ptr = plugin.OnPromoContextRendering(plugin_ctx);
    std::optional<handlers::PromoContext> promo_context;
    routestats::plugins::common::ResultWrapper<
        std::optional<handlers::PromoContext>>
        result_promo(promo_context);
    promo_ptr->SerializeInPlace(result_promo);

    ASSERT_TRUE(promo_context);
    ASSERT_TRUE(promo_context->shuttle);
    const auto& shuttle_promo_ctx = *promo_context->shuttle;

    ASSERT_EQ(shuttle_promo_ctx.eta_seconds, 240);
    ASSERT_EQ(shuttle_promo_ctx.offer_id, kShortcutOfferId);
  });
}

TEST(TestShuttleOrderFlowPlugin, ShortcutGoodCaseOfferV2) {
  RunInCoro([]() {
    auto context =
        MakeContext(kTestDataDir + "/only_backend_context.json", true);

    clients::shuttle_control::ShuttleControlClient client(
        [](const clients::shuttle_control::Request& req,
           const clients::shuttle_control::CommandControl&)
            -> clients::shuttle_control::Response {
          CheckRequestShortcut(req);
          auto resp = LoadJsonFromFile(kTestDataDir + "/v1_match_response.json")
                          .As<clients::shuttle_control::Response>();
          return resp;
        });
    context.clients.shuttle_control = routestats::core::MakeClient(
        static_cast<clients::shuttle_control::Client&>(std::ref(client)));
    context.rendering.translator = std::make_shared<test::TranslatorMock>(
        [](const core::Translation& translation,
           const std::string&) -> std::optional<std::string> {
          static const std::unordered_map<std::string, std::string>
              kTranslations = {{"summary.shuttle.requirement_selector.title",
                                "Количество мест"},
                               {"summary.shuttle.requirement_selector.subtitle",
                                "Будет в шаттле через 5 минут"}};

          const auto it = kTranslations.find(translation->main_key.key);
          if (it != kTranslations.end()) {
            return it->second;
          }

          return std::nullopt;
        });

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    plugins::top_level::ShuttleOrderFlowPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "shuttle";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    extensions.at("shuttle")->Apply("shuttle", level);
    ASSERT_TRUE(level.is_hidden);
    ASSERT_FALSE(level.is_hidden.value());
    ASSERT_FALSE(level.tariff_unavailable);

    const auto level_ptr = plugin.OnServiceLevelRendering(level, plugin_ctx);

    handlers::ServiceLevel handlers_level;
    routestats::plugins::common::ResultWrapper<handlers::ServiceLevel> result(
        handlers_level);
    level_ptr->SerializeInPlace(result);

    ASSERT_TRUE(handlers_level.shuttle_extra);

    const auto& extra = *handlers_level.shuttle_extra;
    ASSERT_EQ(extra.offers.size(), 1);

    const auto& offer = extra.offers.front();
    const auto& v2_offer = std::get<::handlers::ShuttleOfferV2>(offer);

    ASSERT_EQ(v2_offer.shuttle_id, "shortcut_shuttle");
    ASSERT_EQ(v2_offer.route_id, "gkZxnYQ73QGqrKyz");
    ASSERT_EQ(v2_offer.pickup_stop_id, "shortcut_pickup_stop");
    ASSERT_EQ(v2_offer.dropoff_stop_id, "shortcut_dropoff_stop");
    ASSERT_EQ(v2_offer.offer_id, kShortcutOfferId);

    const auto& requirement_selector = v2_offer.requirement_selector;
    ASSERT_TRUE(requirement_selector.has_value());
    ASSERT_EQ(requirement_selector->icon_tag, "clock");
    ASSERT_EQ(requirement_selector->title.text, "Количество мест");
    ASSERT_EQ(requirement_selector->title.color, "#345678");
    ASSERT_TRUE(requirement_selector->subtitle.has_value());
    ASSERT_EQ(requirement_selector->subtitle->text,
              "Будет в шаттле через 5 минут");
    ASSERT_EQ(requirement_selector->subtitle->color, "#00bb00");
    ASSERT_TRUE(requirement_selector->is_passengers_counter_visible);

    auto promo_ptr = plugin.OnPromoContextRendering(plugin_ctx);
    std::optional<handlers::PromoContext> promo_context;
    routestats::plugins::common::ResultWrapper<
        std::optional<handlers::PromoContext>>
        result_promo(promo_context);
    promo_ptr->SerializeInPlace(result_promo);

    ASSERT_TRUE(promo_context);
    ASSERT_TRUE(promo_context->shuttle);
    const auto& shuttle_promo_ctx = *promo_context->shuttle;

    ASSERT_EQ(shuttle_promo_ctx.eta_seconds, 240);
    ASSERT_EQ(shuttle_promo_ctx.offer_id, kShortcutOfferId);
  });
}

TEST(TestShuttleOrderFlowPlugin, ShortcutGoodCasePartialOfferV2) {
  RunInCoro([]() {
    auto context =
        MakeContext(kTestDataDir + "/only_backend_context.json", true);

    clients::shuttle_control::ShuttleControlClient client(
        [](const clients::shuttle_control::Request& req,
           const clients::shuttle_control::CommandControl&)
            -> clients::shuttle_control::Response {
          CheckRequestShortcut(req);
          auto resp =
              LoadJsonFromFile(kTestDataDir + "/v1_match_response_partial.json")
                  .As<clients::shuttle_control::Response>();
          return resp;
        });
    context.clients.shuttle_control = routestats::core::MakeClient(
        static_cast<clients::shuttle_control::Client&>(std::ref(client)));
    context.rendering.translator = std::make_shared<test::TranslatorMock>(
        [](const core::Translation& translation,
           const std::string&) -> std::optional<std::string> {
          static const std::unordered_map<std::string, std::string>
              kTranslations = {
                  {"summary.shuttle.disabled_requirement_selector.title",
                   "Количество мест"},
                  {"summary.shuttle.disabled_requirement_selector.subtitle",
                   "Сейчас свободных мест нет"},
                  {"routestats.tariff_unavailable.no_shuttle_seats_available",
                   "Забронировать"}};

          const auto it = kTranslations.find(translation->main_key.key);
          if (it != kTranslations.end()) {
            return it->second;
          }

          return std::nullopt;
        });

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    plugins::top_level::ShuttleOrderFlowPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "shuttle";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    extensions.at("shuttle")->Apply("shuttle", level);
    ASSERT_TRUE(level.is_hidden);
    ASSERT_FALSE(level.is_hidden.value());
    ASSERT_TRUE(level.tariff_unavailable);

    const auto level_ptr = plugin.OnServiceLevelRendering(level, plugin_ctx);

    handlers::ServiceLevel handlers_level;
    routestats::plugins::common::ResultWrapper<handlers::ServiceLevel> result(
        handlers_level);
    level_ptr->SerializeInPlace(result);

    ASSERT_TRUE(handlers_level.shuttle_extra);

    const auto& extra = *handlers_level.shuttle_extra;
    ASSERT_EQ(extra.offers.size(), 1);

    const auto& offer = extra.offers.front();
    const auto& v2_offer = std::get<::handlers::ShuttleOfferV2>(offer);

    ASSERT_FALSE(v2_offer.shuttle_id.has_value());
    ASSERT_EQ(v2_offer.route_id, "gkZxnYQ73QGqrKyz");
    ASSERT_EQ(v2_offer.pickup_stop_id, "shuttle-stop-Pmp80rQ23L4wZYxd");
    ASSERT_EQ(v2_offer.dropoff_stop_id, "shuttle-stop-VlAK13MzaLx6Bmnd");
    ASSERT_EQ(v2_offer.offer_id, kShortcutOfferId);

    const auto& requirement_selector = v2_offer.requirement_selector;
    ASSERT_TRUE(requirement_selector.has_value());
    ASSERT_FALSE(requirement_selector->icon_tag.has_value());
    ASSERT_EQ(requirement_selector->title.text, "Количество мест");
    ASSERT_EQ(requirement_selector->title.color, "#345678");
    ASSERT_TRUE(requirement_selector->subtitle.has_value());
    ASSERT_EQ(requirement_selector->subtitle->text,
              "Сейчас свободных мест нет");
    ASSERT_EQ(requirement_selector->subtitle->color, "#00bb00");
    ASSERT_FALSE(requirement_selector->is_passengers_counter_visible);

    auto promo_ptr = plugin.OnPromoContextRendering(plugin_ctx);
    std::optional<handlers::PromoContext> promo_context;
    routestats::plugins::common::ResultWrapper<
        std::optional<handlers::PromoContext>>
        result_promo(promo_context);
    ASSERT_FALSE(promo_context);
  });
}

TEST(TestShuttleOrderFlowPlugin, CasePartialV2OfferToV1Client) {
  RunInCoro([]() {
    auto context =
        MakeContext(kTestDataDir + "/only_backend_context.json", false);

    clients::shuttle_control::ShuttleControlClient client(
        [](const clients::shuttle_control::Request& req,
           const clients::shuttle_control::CommandControl&)
            -> clients::shuttle_control::Response {
          CheckRequestShortcut(req);
          auto resp =
              LoadJsonFromFile(kTestDataDir + "/v1_match_response_partial.json")
                  .As<clients::shuttle_control::Response>();
          return resp;
        });
    context.clients.shuttle_control = routestats::core::MakeClient(
        static_cast<clients::shuttle_control::Client&>(std::ref(client)));

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    plugins::top_level::ShuttleOrderFlowPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "shuttle";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    extensions.at("shuttle")->Apply("shuttle", level);
    ASSERT_TRUE(level.is_hidden);
    ASSERT_TRUE(level.is_hidden.value());
    ASSERT_FALSE(level.tariff_unavailable);

    const auto level_ptr = plugin.OnServiceLevelRendering(level, plugin_ctx);
    ASSERT_FALSE(level_ptr);
  });
}

TEST(TestShuttleOrderFlowPlugin, ShortcutBadCase) {
  RunInCoro([]() {
    auto context = MakeContext(kTestDataDir + "/only_backend_context.json");

    clients::shuttle_control::ShuttleControlClient client(
        [](const clients::shuttle_control::Request& req,
           const clients::shuttle_control::CommandControl&) {
          CheckRequestShortcut(req);
          auto resp =
              LoadJsonFromFile(kTestDataDir + "/v1_match_response_empty.json")
                  .As<clients::shuttle_control::Response>();
          return resp;
        });
    context.clients.shuttle_control = routestats::core::MakeClient(
        static_cast<clients::shuttle_control::Client&>(std::ref(client)));

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    plugins::top_level::ShuttleOrderFlowPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "shuttle";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    extensions.at("shuttle")->Apply("shuttle", level);

    ASSERT_TRUE(level.is_hidden);
    ASSERT_FALSE(*level.is_hidden);
    ASSERT_TRUE(level.paid_options);
    ASSERT_TRUE(level.paid_options->color_button);
    ASSERT_TRUE(level.tariff_unavailable);
    const auto& item = *level.tariff_unavailable;
    ASSERT_EQ(item.code, "no_shuttles_left");
    ASSERT_EQ(item.message,
              "routestats.tariff_unavailable.no_shuttles_left##ru");

    ASSERT_TRUE(item.order_button_action);
    const auto unavailable_action =
        std::get_if<routestats::core::TypedDeeplinkAction>(
            &*item.order_button_action);
    ASSERT_TRUE(unavailable_action) << "bad variant";
    ASSERT_EQ(unavailable_action->deeplink, "yataxi://ololo");

    ASSERT_TRUE(level.summary_style);
    ASSERT_TRUE(level.summary_style->order_button);
    ASSERT_EQ(level.summary_style->order_button->text_color, "#dd1234");
    const auto unavailable_action_button_fill =
        std::get_if<routestats::core::SolidColor>(
            &level.summary_style->order_button->fill);
    ASSERT_TRUE(unavailable_action_button_fill) << "bad variant";
    ASSERT_EQ(unavailable_action_button_fill->color, "#abcdef");

    const auto level_ptr = plugin.OnServiceLevelRendering(level, plugin_ctx);
    ASSERT_FALSE(level_ptr);
  });
}

TEST(TestShuttleOrderFlowPlugin, ShortcutOutOfSchedule) {
  RunInCoro([]() {
    auto context = MakeContext(kTestDataDir + "/only_backend_context.json");

    // Override mock time set inside of MakeContext
    // 11 Apr 2022 00:00:30 MSK
    utils::datetime::MockNowSet(std::chrono::system_clock::time_point{
        std::chrono::seconds{1649624430}});

    clients::shuttle_control::ShuttleControlClient client(
        [](const clients::shuttle_control::Request& req,
           const clients::shuttle_control::CommandControl&) {
          CheckRequestShortcut(req);
          auto resp =
              LoadJsonFromFile(kTestDataDir + "/v1_match_response_empty.json")
                  .As<clients::shuttle_control::Response>();
          return resp;
        });
    context.clients.shuttle_control = routestats::core::MakeClient(
        static_cast<clients::shuttle_control::Client&>(std::ref(client)));

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    plugins::top_level::ShuttleOrderFlowPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "shuttle";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    extensions.at("shuttle")->Apply("shuttle", level);

    ASSERT_TRUE(level.is_hidden);
    ASSERT_FALSE(*level.is_hidden);
    ASSERT_TRUE(level.tariff_unavailable);
    const auto& item = *level.tariff_unavailable;
    ASSERT_EQ(item.code, "out_of_schedule");
    ASSERT_EQ(item.message,
              "routestats.tariff_unavailable.out_of_schedule##ru");

    const auto level_ptr = plugin.OnServiceLevelRendering(level, plugin_ctx);
    ASSERT_FALSE(level_ptr);
  });
}

TEST(TestShuttleOrderFlowPlugin, TariffCardBullets) {
  RunInCoro([]() {
    auto context = MakeContext(kTestDataDir + "/only_backend_context.json");

    clients::shuttle_control::ShuttleControlClient client(
        [](const clients::shuttle_control::Request& req,
           const clients::shuttle_control::CommandControl&) {
          CheckRequestShortcut(req);
          auto resp =
              LoadJsonFromFile(kTestDataDir + "/v1_match_response_empty.json")
                  .As<clients::shuttle_control::Response>();
          return resp;
        });
    context.clients.shuttle_control = routestats::core::MakeClient(
        static_cast<clients::shuttle_control::Client&>(std::ref(client)));

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    plugins::top_level::ShuttleOrderFlowPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "shuttle";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    extensions.at("shuttle")->Apply("shuttle", level);

    ASSERT_TRUE(level.tariff_card.has_value());

    auto tariff_card = level.tariff_card.value();

    ASSERT_EQ(tariff_card.bullets.size(), 2);
  });
}

TEST(TestShuttleOrderFlowPlugin, ClientContext) {
  RunInCoro([]() {
    auto context = MakeContext(kTestDataDir + "/only_client_context.json");

    clients::shuttle_control::ShuttleControlClient client(
        [](const clients::shuttle_control::Request& req,
           const clients::shuttle_control::CommandControl&) {
          CheckRequestClientContext(req);
          auto resp =
              LoadJsonFromFile(kTestDataDir + "/v1_match_response_empty.json")
                  .As<clients::shuttle_control::Response>();
          return resp;
        });
    context.clients.shuttle_control = routestats::core::MakeClient(
        static_cast<clients::shuttle_control::Client&>(std::ref(client)));

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    plugins::top_level::ShuttleOrderFlowPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "shuttle";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    extensions.at("shuttle")->Apply("shuttle", level);
  });
}

}  // namespace routestats::full::shuttle_order_flow
