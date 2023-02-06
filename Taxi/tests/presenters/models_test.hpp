#pragma once

#include <handlers/4.0/sweet-home/v1/sdk-state/post/response.hpp>

namespace sweet_home::tests::handlers {

::handlers::ActionButton MakeActionButton(
    const std::optional<std::string>& title,
    const std::optional<std::string>& subtitle,
    const ::handlers::ActionButtonAction& action =
        ::handlers::ActionButtonAction::kPlusBuy,
    std::optional<std::vector<::handlers::ActionButtonState>> states =
        std::vector<::handlers::ActionButtonState>{
            {::handlers::ActionButtonStateState::kIdle, "Попробовать бесплатно",
             std::nullopt}});

}  // namespace sweet_home::tests::handlers

namespace sweet_home::action_button {

void AssertActionButton(const std::optional<::handlers::ActionButton>& left,
                        const std::optional<::handlers::ActionButton>& right);

}  // namespace sweet_home::action_button
