#pragma once

#include <functional>

// run cb in coroutine for USERVER and in current thread otherwise
void TestInEnv(std::function<void()> cb);
