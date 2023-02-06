#include <gtest/gtest.h>

#include <driver-id/dbid_uuid.hpp>
#include <driver-id/driver_id_view_storage.hpp>
#include <driver-id/test/print_to.hpp>

#include <gtest/gtest.h>

namespace driver_id::test {

TEST(DriverIdViewStorage, GetDriverView) {
  DriverIdViewStorage<DriverDbidUndscrUuid> storage;

  DriverDbidUndscrUuid ref{"abc_def"};
  DriverDbidUndscrUuid du2{ref};

  auto view1 = storage.GetDriverView(std::move(du2));

  EXPECT_EQ(view1, ref);

  // Check that same object result is bit-level same view
  DriverDbidUndscrUuid du3{ref};
  auto view2 = storage.GetDriverView(std::move(du3));
  EXPECT_EQ(view1.GetDbid().data(), view2.GetDbid().data());
  EXPECT_EQ(view1.GetUuid().data(), view2.GetUuid().data());
  EXPECT_EQ(view1.GetDbid().size(), view2.GetDbid().size());
  EXPECT_EQ(view1.GetUuid().size(), view2.GetUuid().size());

  // different objects - different hash
  DriverDbidUndscrUuid du4{"efg_hjk"};
  auto view3 = storage.GetDriverView(std::move(du4));
  EXPECT_NE(view1.GetDbid().data(), view3.GetDbid().data());
  EXPECT_NE(view1.GetUuid().data(), view3.GetDbid().data());
}

TEST(DriverIdViewStorage, EqualTo) {
  DriverIdViewStorage<DriverDbidUndscrUuid> storage;
  DriverDbidUndscrUuid ref{"abc_def"};
  DriverDbidUndscrUuid du2{ref};
  DriverDbidUndscrUuid du3{ref};
  DriverDbidUndscrUuid du4{"efg_hjk"};

  auto view1 = storage.GetDriverView(std::move(du2));
  auto view2 = storage.GetDriverView(std::move(du3));

  auto eto = storage.CreateEqualTo();
  EXPECT_TRUE(eto(view1, view2));

  auto view3 = storage.GetDriverView(std::move(du4));
  EXPECT_FALSE(eto(view1, view3));
}

TEST(DriverIdViewStorage, Hash) {
  DriverIdViewStorage<DriverDbidUndscrUuid> storage;
  DriverDbidUndscrUuid ref{"abc_def"};
  DriverDbidUndscrUuid du2{ref};
  DriverDbidUndscrUuid du3{ref};
  DriverDbidUndscrUuid du4{"efg_hjk"};

  auto view1 = storage.GetDriverView(std::move(du2));
  auto view2 = storage.GetDriverView(std::move(du3));

  auto hasher = storage.CreateHasher();
  EXPECT_EQ(hasher(view1), hasher(view2));

  auto view3 = storage.GetDriverView(std::move(du4));
  EXPECT_TRUE((hasher(view1) != hasher(view3)) || (view1 != view3));
}

}  // namespace driver_id::test
