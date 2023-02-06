#pragma once

#include <handlers/base.hpp>
#include <models/unique_drivers.hpp>

namespace handlers {
namespace driver {

class ReactionTestResult : public AuthorizedDriverBase {
 public:
  explicit ReactionTestResult(fastcgi::ComponentContext* context)
      : AuthorizedDriverBase(context, flags::kDefault | flags::kPollingDelay) {}

  void onLoad() override;
  void onUnload() override;

  std::string HandleRequestThrow(fastcgi::Request& request,
                                 const std::string& request_body,
                                 Context& context,
                                 TimeStorage& ts) const override;

 private:
  const utils::DataProvider<models::UniqueDrivers>* unique_drivers_ = nullptr;
  utils::mongo::PoolPtr status_history_;
};

}  // namespace driver
}  // namespace handlers
