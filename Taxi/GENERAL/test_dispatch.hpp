#pragma once

#include <components/dispatch_repository.hpp>

#include "dispatch.hpp"

namespace grocery_dispatch::controllers {

// Dispatch implementation for testing purposes
class TestDispatch : public BaseDispatch {
 public:
  constexpr static const std::string_view kName = "test";

 public:
  TestDispatch(controllers::BaseDispatchContext ctx,
               grocery_dispatch::components::DispatchRepository& repo);

  // Name of dispatch type
  std::string_view GetName() const override { return kName; }

  models::DispatchState Schedule() const override;

  models::StatusAndFailureReason Accept() const override;

  models::DispatchState NotifyOrderAssembled() const override;

  models::StatusAndFailureReason Cancel() const override;

  models::DispatchState Status() const override;

  std::optional<models::PerformerContact> PerformerContact() const override;

  void UpdateRescheduleSpecificFields(models::OrderInfo& info) const override;

  std::optional<bool> IsScheduled() const override { return true; }

  bool NeedRescheduleForOrderReady() const override;

 private:
  grocery_dispatch::components::DispatchRepository& repo_;
};

}  // namespace grocery_dispatch::controllers
