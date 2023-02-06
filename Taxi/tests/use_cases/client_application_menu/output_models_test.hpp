#pragma once

#include "use_cases/client_application_menu/output_models.hpp"

namespace sweet_home::tests::output_models {

namespace use_case = sweet_home::client_application_menu;

use_case::output_models::BalanceBadge MakeBalanceBadge(
    bool show_glyph, std::string subtitle,
    std::optional<std::string> placeholder = std::nullopt);

use_case::output_models::Element MakeLead(
    const std::string& title_key,
    const std::optional<std::string>& subtitle_key = std::nullopt,
    client_application::ElementStyle style =
        client_application::ElementStyle::kDefault);

use_case::output_models::Element MakeTrail(
    client_application::ElementStyle style,
    const std::optional<std::string>& title_key = std::nullopt,
    const std::optional<std::string>& subtitle_key = std::nullopt);

use_case::output_models::Element MakeElement(
    const std::optional<std::string>& title_key,
    const std::optional<std::string>& subtitle_key = std::nullopt,
    client_application::ElementStyle style =
        client_application::ElementStyle::kDefault);

use_case::output_models::MenuItem MakeListMenuItem(
    const use_case::output_models::Element& lead,
    const std::optional<use_case::output_models::Element>& trail =
        std::nullopt);

use_case::output_models::Section MakeSection(
    const std::vector<use_case::output_models::MenuItem>& items,
    const client_application::SectionStyle& style =
        client_application::SectionStyle::kNone,
    const std::optional<std::string>& title_key = std::nullopt);

}  // namespace sweet_home::tests::output_models
