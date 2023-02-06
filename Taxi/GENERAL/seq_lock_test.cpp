#include "seq_lock.hpp"

#include <gtest/gtest.h>

#include <chrono>
#include <thread>

using utils::SeqLock;
using utils::SeqLockReadGuard;
using utils::SeqLockWriteGuard;

TEST(SeqLock, SingleReader) {
  SeqLock sq;
  SeqLockReadGuard lock(sq);

  EXPECT_FALSE(lock.MustRetry());
}

TEST(SeqLock, SingleWriter) {
  SeqLock sq;

  SeqLockWriteGuard lock(sq);

  EXPECT_EQ(true, true);  // just to be sure TEST exists OK
}

TEST(SeqLock, ReadRead) {
  SeqLock sq;
  SeqLockReadGuard lock1(sq);
  SeqLockReadGuard lock2(sq);

  EXPECT_FALSE(lock2.MustRetry());
  EXPECT_FALSE(lock1.MustRetry());
}

TEST(SeqLock, ReadReadReverseOrder) {
  SeqLock sq;
  SeqLockReadGuard lock1(sq);
  SeqLockReadGuard lock2(sq);

  EXPECT_FALSE(lock1.MustRetry());
  EXPECT_FALSE(lock2.MustRetry());
}

TEST(SeqLock, ReadWrite) {
  SeqLock sq;
  long counter;

  {
    SeqLockWriteGuard lock(sq);
    EXPECT_FALSE(SeqLockReadGuard::MayEnter(sq, counter));
  }
  EXPECT_TRUE(SeqLockReadGuard::MayEnter(sq, counter));
}

TEST(SeqLock, ReadWriteConflict) {
  SeqLock sq;
  SeqLockReadGuard r(sq);

  { SeqLockWriteGuard w(sq); }

  EXPECT_TRUE(r.MustRetry());
}

TEST(SeqLock, ReadWriteConflictMultiple) {
  SeqLock sq;
  SeqLockReadGuard r(sq);

  { SeqLockWriteGuard w(sq); }
  { SeqLockWriteGuard w(sq); }

  EXPECT_TRUE(r.MustRetry());

  SeqLockReadGuard r2(sq);
  EXPECT_FALSE(r2.MustRetry());
}
