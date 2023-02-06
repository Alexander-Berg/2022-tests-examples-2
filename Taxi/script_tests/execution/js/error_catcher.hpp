#pragma once

#include <optional>
#include <string>

#include <js/execution/interface.hpp>

namespace driver_scoring::admin::script_tests::execution::js {

struct ErrorCatcher final : ::js::execution::ErrorProcessor {
  mutable std::optional<std::string> caught;

  // To catch a JS exception we cannot rely on exception itself because it
  // already has formatted message; this is a way to catch exception from V8 on
  // our own
  ::js::execution::ErrorProcessor::ProcessResult Process(
      const v8::TryCatch& try_catch) const override;

  // Returns what was caught last and flushes it
  std::optional<std::string> PopError();
};

}  // namespace driver_scoring::admin::script_tests::execution::js
