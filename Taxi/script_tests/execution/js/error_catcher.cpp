#include "error_catcher.hpp"

namespace driver_scoring::admin::script_tests::execution::js {

::js::execution::ErrorProcessor::ProcessResult ErrorCatcher::Process(
    const v8::TryCatch& try_catch) const {
  caught = ::js::ToString(try_catch.Exception());
  return {};
}

std::optional<std::string> ErrorCatcher::PopError() {
  std::optional<std::string> res{std::nullopt};
  std::swap(res, caught);
  return res;
}

}  // namespace driver_scoring::admin::script_tests::execution::js
