#pragma once
#include <components/cron.hpp>
#include <handlers/base.hpp>
#include <models/constants.hpp>
#include <psql/component.hpp>

namespace handlers {
namespace service {

class TestsControlHandler
    : public ContextBase,
      public components::NamedComponentMixIn<TestsControlHandler> {
 public:
  static constexpr const char* name = "tests-control-handler";

  using ContextBase::ContextBase;
  void onLoad() override;
  void onUnload() override;
  std::string HandleRequestThrow(fastcgi::Request& request,
                                 const std::string& request_body,
                                 handlers::Context& context) const override;

 private:
  components::Cron::CPtr cron_;
  mutable components::Psql::Ptr psql_;
};

}  // namespace service
}  // namespace handlers
