#include <userver/utest/utest.hpp>

#include <eventus/sources/logbroker_source/offsets_storage.hpp>

using namespace eventus::sources::logbroker_source;

namespace {

OffsetsStorage::ValueType duplicate(int x) {
  return {uint64_t(x), uint32_t(x)};
}

}  // namespace

TEST(OffsetStorage, basic) {
  OffsetsStorage storage{3};
  for (int i = 0; i < 6; i++) {
    ASSERT_TRUE(storage.Insert(duplicate(i)));
  }

  for (int i = 0; i < 2; i++) {
    for (int j = 4; j < 6; j++) {
      ASSERT_FALSE(storage.Insert(duplicate(j)));
    }
  }

  ASSERT_TRUE(storage.Insert(duplicate(6)));
}

TEST(OffsetStorage, removal_order) {
  OffsetsStorage storage{5};
  for (int i = 5; i >= 0; i--) {
    ASSERT_TRUE(storage.Insert(duplicate(i)));
  }

  for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 5; j++) {
      ASSERT_FALSE(storage.Insert(duplicate(j)));
    }
  }
  ASSERT_TRUE(storage.Insert(duplicate(5)));

  ASSERT_FALSE(storage.Insert(duplicate(0)));
  ASSERT_TRUE(storage.Insert(duplicate(4)));
}
