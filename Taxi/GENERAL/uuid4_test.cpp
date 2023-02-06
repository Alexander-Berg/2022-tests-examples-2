#include <gtest/gtest.h>

#include "utils/uuid4.hpp"

#include <atomic>

#include <boost/thread/mutex.hpp>
#include <boost/thread/thread.hpp>

const size_t kThreads = 512;
const size_t kCount = kThreads * 100;

TEST(Uuid4, Simple) {
  std::set<std::string> set;
  for (size_t i = 0; i < kCount; ++i) {
    set.insert(utils::generators::Uuid4());
  }

  EXPECT_EQ(kCount, set.size());  // all values are unique
}

TEST(Uuid4, Multithreads) {
  boost::mutex mutex;
  std::set<std::string> set;
  std::atomic<size_t> count(0);

  boost::thread_group threads;
  for (size_t i = 0; i < kThreads; ++i) {
    threads.create_thread([&]() -> void {
      std::set<std::string> tset;
      while (count++ < kCount) {
        tset.insert(utils::generators::Uuid4());
      }
      boost::mutex::scoped_lock guard(mutex);
      set.insert(tset.begin(), tset.end());
    });
  }
  threads.join_all();

  EXPECT_EQ(kCount, set.size());  // all values are unique
}
