#include <trackstory-shorttracks/scoped_lock.hpp>
#include <userver/concurrent/variable.hpp>
#include <userver/utils/async.hpp>

#include <userver/utest/utest.hpp>

UTEST(ScopedLock, BasicTesting) {
  concurrent::Variable<int> var1{41};
  concurrent::Variable<int> var2{42};
  concurrent::Variable<int> var3{43};
  concurrent::Variable<int> var4{44};

  {
    trackstory::shorttracks::details::ScopedLock scoped_lk(var1, var2, var3);
    auto [var1_ptr, var2_ptr, var3_ptr] = scoped_lk.GetDataPointers();
    *var1_ptr = 61;
    *var2_ptr = 62;
    *var3_ptr = 63;

    auto try_lock1 = var1.UniqueLock(std::try_to_lock);
    auto try_lock2 = var2.UniqueLock(std::try_to_lock);
    auto try_lock3 = var3.UniqueLock(std::try_to_lock);
    auto try_lock4 = var4.UniqueLock(std::try_to_lock);

    ASSERT_FALSE(try_lock1);
    ASSERT_FALSE(try_lock2);
    ASSERT_FALSE(try_lock3);
    ASSERT_TRUE(try_lock4);
  }

  auto try_lock1 = var1.UniqueLock(std::try_to_lock);
  auto try_lock2 = var2.UniqueLock(std::try_to_lock);
  auto try_lock3 = var3.UniqueLock(std::try_to_lock);
  auto try_lock4 = var4.UniqueLock(std::try_to_lock);

  ASSERT_TRUE(try_lock1);
  ASSERT_TRUE(try_lock2);
  ASSERT_TRUE(try_lock3);
  ASSERT_TRUE(try_lock4);

  ASSERT_EQ(**try_lock1, 61);
  ASSERT_EQ(**try_lock2, 62);
  ASSERT_EQ(**try_lock3, 63);
  ASSERT_EQ(**try_lock4, 44);
}
