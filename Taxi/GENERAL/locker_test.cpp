#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "locker.hpp"

namespace graph::test {

namespace {
static size_t kPoolSize = 1;
}

UTEST(TestLocker, ExceptionOnLock) {
  internal::Pool pool(kPoolSize);

  internal::PoolLocker locker(pool);
  auto createAnotherLocker = [&pool] { internal::PoolLocker locker(pool); };
  EXPECT_THROW(createAnotherLocker(), std::runtime_error);
}

}  // namespace graph::test
