#pragma once

#include <string>
#include <utils/future.hpp>

#include <defs/definitions/admin.hpp>

namespace driver_scoring::admin::script_tests {

using Status = ::handlers::ScriptTestStatus;

using Result = ::handlers::ScriptTestResult;

using FutureType = utils::Future<Result>;

using PromiseType = utils::Promise<Result>;

}  // namespace driver_scoring::admin::script_tests
