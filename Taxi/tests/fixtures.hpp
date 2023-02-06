#pragma once

#include <defs/all_definitions.hpp>
#include "components/blocks.hpp"
#include "components/experiment_based_parameters.hpp"
#include "models/entrypoints.hpp"
#include "models/scenarios.hpp"

namespace fixtures {

handlers::GridCell BuildCell(
    const shortcuts::scenarios::ShortcutScenario& scenario);

models::InternalBrick BuildInternalBrick(
    const shortcuts::scenarios::ShortcutScenario& scenario);

models::InternalButton BuildInternalButton(
    const shortcuts::scenarios::ShortcutScenario& scenario);

std::vector<handlers::GridCell> BuildFakeCells();

std::vector<handlers::ButtonObject> BuildFakeButtons();
handlers::SectionHeader BuildFakeShopHeader();

std::vector<handlers::OfferItemObject> BuildFakeOfferItems();

std::vector<blocks::Block> BuildFakeBlocks(int amount);

std::vector<models::InternalBrick> BuildFakeInternalBricks();

std::vector<models::InternalButton> BuildFakeInternalButtons();
std::vector<models::InternalButton> BuildFakeInternalShopButtons();

shortcuts::experiments::BlockAppearance BuildBlockAppearance(
    const std::optional<std::vector<std::string>>& tags,
    const std::optional<std::vector<std::string>>& tags_to_previous);

shortcuts::experiments::ExperimentBasedParameters
BuildExperimentBasedParameters(
    const shortcuts::experiments::BlocksMap& blocks_map,
    const std::optional<experiments3::ShortcutsSectionsSettings::Value>&
        section_settings);
}  // namespace fixtures
