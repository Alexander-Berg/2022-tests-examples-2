#pragma once

#include <common/fwd.hpp>
#include <handlers/tvm2.hpp>

namespace antifraud {
namespace handlers {
namespace rules {

class TestHandler final : public ::handlers::TVM2Handler {
 public:
  using TVM2Handler::TVM2Handler;

 private:
  void onLoad() final;
  void onUnload() final;
  void HandleRequestThrowTVM2Checked(fastcgi::Request& request,
                                     ::handlers::BaseContext& context) final;

  ::components::V8* v8_component_{};
  config::Component* config_{};
};

}  // namespace rules
}  // namespace handlers
}  // namespace antifraud
