#include <userver/utest/utest.hpp>

#include <userver/formats/json.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <components/experiment_based_parameters/header.hpp>

namespace {

shortcuts::experiments::HeaderElementAppearance DeserializeAppearanceFromJson(
    const std::optional<std::string>& deeplink,
    const std::optional<std::string>& deathbrick_deeplink) {
  auto json_builder = formats::json::ValueBuilder(formats::json::FromString(R"({
        "title_key": "",
        "background_color": "",
        "active_text_color": "",
        "disabled_text_color": "",
        "icon_tag": "",
        "multicolor_icon": {"enabled_tag": "", "disabled_tag": ""}
    })"));

  if (deeplink.has_value()) {
    json_builder["deeplink"] = deeplink.value();
  }

  if (deathbrick_deeplink.has_value()) {
    json_builder["deathbrick_deeplink"] = deathbrick_deeplink.value();
  }

  return json_builder.ExtractValue()
      .As<shortcuts::experiments::HeaderElementAppearance>();
}

void CheckDeeplinks(
    const shortcuts::experiments::HeaderElementAppearance& appearance,
    const ::std::optional<::std::string>& expected_deeplink,
    const ::std::optional<::std::string>& expected_deathbrick_deeplink) {
  ASSERT_EQ(expected_deeplink, appearance.deeplink);
  ASSERT_EQ(expected_deathbrick_deeplink, appearance.deathbrick_deeplink);
}

}  // namespace

TEST(TestDeserialization, AppearanceDeeplinkDeserialization) {
  RunInCoro(
      [] {
        shortcuts::experiments::HeaderElementAppearance appearance;

        appearance =
            DeserializeAppearanceFromJson(::std::nullopt, ::std::nullopt);
        CheckDeeplinks(appearance, ::std::nullopt, ::std::nullopt);

        appearance =
            DeserializeAppearanceFromJson({"deeplink"}, ::std::nullopt);
        CheckDeeplinks(appearance, {"deeplink"}, ::std::nullopt);

        appearance = DeserializeAppearanceFromJson(::std::nullopt,
                                                   {"deathbrick_deeplink"});
        CheckDeeplinks(appearance, ::std::nullopt, {"deathbrick_deeplink"});

        appearance = DeserializeAppearanceFromJson({"deeplink"},
                                                   {"deathbrick_deeplink"});
        CheckDeeplinks(appearance, {"deeplink"}, {"deathbrick_deeplink"});
      },
      1);
}
