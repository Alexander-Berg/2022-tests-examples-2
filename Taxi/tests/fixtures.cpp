#include "fixtures.hpp"
#include "views/v1/blender-shortcuts/post/view.hpp"

#include <fmt/format.h>

namespace fixtures {

handlers::GridCell BuildCell(
    const shortcuts::scenarios::ShortcutScenario& scenario) {
  handlers::GridCell cell;
  cell.shortcut.scenario = scenario;
  return cell;
}

models::InternalBrick BuildInternalBrick(
    const shortcuts::scenarios::ShortcutScenario& scenario) {
  models::InternalBrick brick;
  brick.scenario = scenario;
  return brick;
}

models::InternalButton BuildInternalButton(
    const shortcuts::scenarios::ShortcutScenario& scenario) {
  models::InternalButton button;
  button.scenario = scenario;
  return button;
}

std::vector<handlers::GridCell> BuildFakeCells() {
  return std::vector<handlers::GridCell>{
      BuildCell(shortcuts::scenarios::kTaxiExpectedDestination),
      BuildCell(shortcuts::scenarios::kMediaStories),
      BuildCell(shortcuts::scenarios::kMediaStories),
      BuildCell(shortcuts::scenarios::kEatsPlace),
  };
}

std::vector<handlers::OfferItemObject> BuildFakeOfferItems() {
  return {fixtures::BuildInternalBrick(shortcuts::scenarios::kGroceryCategory)
              .brick};
}

std::vector<handlers::ButtonObject> BuildFakeButtons() {
  std::vector<handlers::ButtonObject> result;
  for (auto internal_button : BuildFakeInternalButtons()) {
    result.push_back(internal_button.button);
  }
  return result;
}

std::vector<blocks::Block> BuildFakeBlocks(int amount) {
  std::vector<blocks::Block> result;
  for (int i = 0; i < amount; i++) {
    result.push_back({BuildFakeCells(), {}, fmt::format("slug_{}", i)});
  }
  return result;
}

std::vector<models::InternalBrick> BuildFakeInternalBricks() {
  return std::vector<models::InternalBrick>{
      BuildInternalBrick(shortcuts::scenarios::kEatsBasedEats),
      BuildInternalBrick(shortcuts::scenarios::kEatsBasedGrocery),
  };
}

std::vector<models::InternalButton> BuildFakeInternalButtons() {
  return std::vector<models::InternalButton>{
      BuildInternalButton(shortcuts::scenarios::kDiscoveryDrive),
      BuildInternalButton(shortcuts::scenarios::kDiscoveryMasstransit),
  };
}

std::vector<models::InternalButton> BuildFakeInternalShopButtons() {
  return std::vector<models::InternalButton>{
      BuildInternalButton(shortcuts::scenarios::kEatsShop),
      BuildInternalButton(shortcuts::scenarios::kEatsShop),
  };
}

handlers::SectionHeader BuildFakeShopHeader() {
  std::vector<extended_template::ATUnit> attributed_text_items{
      extended_template::ATTextProperty{
          handlers::libraries::extended_template::ATTextPropertyType::kText,
          "text"}};
  return handlers::SectionHeader{
      extended_template::AttributedText{attributed_text_items}};
}

shortcuts::experiments::BlockAppearance BuildBlockAppearance(
    const std::optional<std::vector<std::string>>& tags,
    const std::optional<std::vector<std::string>>& tags_to_previous) {
  shortcuts::experiments::BlockAppearance result;
  result.tags = tags;
  result.tags_to_previous = tags_to_previous;
  return result;
}

shortcuts::experiments::ExperimentBasedParameters
BuildExperimentBasedParameters(
    const shortcuts::experiments::BlocksMap& blocks_map,
    const std::optional<experiments3::ShortcutsSectionsSettings::Value>&
        section_settings) {
  shortcuts::experiments::ExperimentBasedParameters result;
  result.blocks_map = blocks_map;
  result.sections_settings = section_settings;
  return result;
}

}  // namespace fixtures
