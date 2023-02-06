#include "in_env_test.hpp"

#ifdef USERVER

#include <utest/utest.hpp>

void TestInEnv(std::function<void()> cb) { TestInCoro(std::move(cb)); }

#else

void TestInEnv(std::function<void()> cb) { cb(); }

#endif
