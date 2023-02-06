#pragma once

#include "internal/action_button/repository.hpp"

#include <functional>

namespace sweet_home::mocks {

using GetActionButtonInfoHandler = std::function<action_button::ActionButton(
    const action_button::Action&, const subscription::PlusSubscription&)>;

class ActionButtonRepositoryMock
    : public action_button::ActionButtonRepository {
 private:
  GetActionButtonInfoHandler handler_get_action_button_;

 public:
  ActionButtonRepositoryMock() {
    handler_get_action_button_ =
        [](const action_button::Action& action,
           const subscription::PlusSubscription& /*subscription*/) {
          action_button::ActionButton result;
          result.action = action;
          return result;
        };
  }
  ActionButtonRepositoryMock(
      const GetActionButtonInfoHandler& handler_get_action_button)
      : handler_get_action_button_(handler_get_action_button) {}

  action_button::ActionButton GetActionButtonInfo(
      const action_button::Action& action,
      const subscription::PlusSubscription& subscription) const override {
    return handler_get_action_button_(action, subscription);
  }
};

}  // namespace sweet_home::mocks
