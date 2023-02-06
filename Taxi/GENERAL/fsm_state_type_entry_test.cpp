#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "fsm_state_type_entry.hpp"

namespace {
namespace drwi = driver_route_watcher::internal;
namespace drwm = driver_route_watcher::models;
}  // namespace

UTEST(fsm_state_type_entry, to_flatbuffers_and_back_to_normal) {
  drwm::FsmStateType state = drwm::FsmStateType::kRouteRequest;

  auto fbs_state = drwi::ToFlatbuffers(state);
  drwm::FsmStateType same_state = drwi::ToFsmStateType(fbs_state);

  ASSERT_EQ(state, same_state);
}
