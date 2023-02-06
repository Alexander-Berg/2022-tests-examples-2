#include "output_models_test.hpp"

namespace sweet_home::tests::output_models {

use_case::output_models::BalanceBadge MakeBalanceBadge(
    bool show_glyph, std::string subtitle,
    std::optional<std::string> placeholder) {
  use_case::output_models::BalanceBadge result;
  result.show_glyph = show_glyph;
  result.subtitle = core::MakeTranslation(core::MakeClientKey(subtitle));

  if (placeholder) {
    result.placeholder =
        core::MakeTranslation(core::MakeClientKey(*placeholder));
  }
  return result;
}

use_case::output_models::Element MakeLead(
    const std::string& title_key,
    const std::optional<std::string>& subtitle_key,
    client_application::ElementStyle style) {
  return MakeElement(title_key, subtitle_key, style);
}

use_case::output_models::Element MakeTrail(
    client_application::ElementStyle style,
    const std::optional<std::string>& title_key,
    const std::optional<std::string>& subtitle_key) {
  return MakeElement(title_key, subtitle_key, style);
}

use_case::output_models::Element MakeElement(
    const std::optional<std::string>& title_key,
    const std::optional<std::string>& subtitle_key,
    client_application::ElementStyle style) {
  use_case::output_models::Element result;
  result.style = style;
  if (title_key) {
    result.title = core::MakeTranslation(core::MakeClientKey(*title_key));
  }
  if (subtitle_key) {
    result.subtitle = core::MakeTranslation(core::MakeClientKey(*subtitle_key));
  }
  // TODO: icon
  return result;
}

use_case::output_models::MenuItem MakeListMenuItem(
    const use_case::output_models::Element& lead,
    const std::optional<use_case::output_models::Element>& trail) {
  actions::Action action;
  action.type = actions::ActionType::kOpenDeeplink;
  action.deeplink = {"this is deeplink for presenters test", std::nullopt};

  use_case::output_models::MenuItem result;
  result.type = client_application::MenuItemType::kListItem;
  result.item_id = "test_list_item";
  result.list_item = {action, lead, trail};
  return result;
}

use_case::output_models::Section MakeSection(
    const std::vector<use_case::output_models::MenuItem>& items,
    const client_application::SectionStyle& style,
    const std::optional<std::string>& title_key) {
  use_case::output_models::Section result;
  result.style = style;
  if (title_key) {
    result.title = core::MakeTranslation(core::MakeClientKey(*title_key));
  }
  result.items = items;
  return result;
}

}  // namespace sweet_home::tests::output_models
