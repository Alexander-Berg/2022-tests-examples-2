#include <gtest/gtest.h>

#include "models_test.hpp"

namespace sweet_home::tests::handlers {

::handlers::ActionButton MakeActionButton(
    const std::optional<std::string>& title,
    const std::optional<std::string>& subtitle,
    const ::handlers::ActionButtonAction& action,
    std::optional<std::vector<::handlers::ActionButtonState>> states) {
  ::handlers::ActionButton result;

  result.title = title;
  result.subtitle = subtitle;
  result.action = action;
  result.states = states;

  return result;
}

}  // namespace sweet_home::tests::handlers

namespace sweet_home::action_button {

void AssertActionButton(const std::optional<::handlers::ActionButton>& left,
                        const std::optional<::handlers::ActionButton>& right) {
  if (!left && !right) {
    SUCCEED();
    return;
  }
  if (!left || !right) {
    FAIL();
    return;
  }
  ASSERT_EQ(left->title, right->title);
  ASSERT_EQ(left->subtitle, right->subtitle);
  ASSERT_EQ(left->action, right->action);

  if (!left->states && !right->states) {
    SUCCEED();
    return;
  }
  if (!left->states || !right->states) {
    FAIL();
    return;
  }
  ASSERT_EQ(left->states->size(), right->states->size());
  for (size_t i = 0; i < left->states->size(); ++i) {
    auto state_left = (*left->states)[i];
    auto state_right = (*left->states)[i];
    ASSERT_EQ(state_left.title, state_right.title);
    ASSERT_EQ(state_left.subtitle, state_right.subtitle);
    ASSERT_EQ(state_left.state, state_right.state);
  }
}

}  // namespace sweet_home::action_button
