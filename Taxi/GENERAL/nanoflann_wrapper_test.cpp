#include <gtest/gtest.h>

#include "nanoflann_wrapper_utils.hpp"

const auto& cloud = utils::nanoflann::tests::GetCloud();
const auto& tree = utils::nanoflann::tests::CreateKDTree();

TEST(NanoflannWrapper, SearchOrigin_1) {
  for (size_t i = 0; i < 64; ++i) {
    utils::nanoflann::tests::SearchCallback callback(1, 10);
    tree->SearchOrigin(cloud[i].position, callback);

    ASSERT_EQ(1, callback.size());

    const auto res = *callback.result().begin();
    EXPECT_EQ(cloud[i].position, res.point);
    EXPECT_EQ(0, res.distance);
  }
}

TEST(NanoflannWrapper, SearchOrigin_1000) {
  for (size_t i = 0; i < 64; ++i) {
    utils::nanoflann::tests::SearchCallback callback(1000, 40000000);
    tree->SearchOrigin(cloud[i].position, callback);
    EXPECT_EQ(1000, callback.size());
  }
}

TEST(NanoflannWrapper, SearchOrigin_0) {
  for (size_t i = 0; i < 64; ++i) {
    utils::nanoflann::tests::SearchCallback callback(0, 30000);
    tree->SearchOrigin(cloud[i].position, callback);
    EXPECT_LT(0, callback.size());
  }
}

TEST(NanoflannWrapper, Search_1) {
  for (size_t i = 0; i < 64; ++i) {
    utils::nanoflann::tests::SearchCallback callback(1, 10);
    tree->Search(cloud[i].position, callback);

    ASSERT_EQ(1, callback.size());

    const auto res = *callback.result().begin();
    EXPECT_EQ(cloud[i].position, res.point);
    EXPECT_EQ(0, res.distance);
  }
}

TEST(NanoflannWrapper, Search_1000) {
  for (size_t i = 0; i < 64; ++i) {
    utils::nanoflann::tests::SearchCallback callback(1000, 40000000);
    tree->Search(cloud[i].position, callback);
    EXPECT_EQ(1000, callback.size());
  }
}

TEST(NanoflannWrapper, Search_0) {
  for (size_t i = 0; i < 64; ++i) {
    utils::nanoflann::tests::SearchCallback callback(0, 30000);
    tree->Search(cloud[i].position, callback);
    EXPECT_LT(0, callback.size());
  }
}

TEST(NanoflannWrapper, SearchVsSearch_1000) {
  for (size_t i = 0; i < 64; ++i) {
    utils::nanoflann::tests::SearchCallback callback1(1000, 40000000);
    utils::nanoflann::tests::SearchCallback callback2(1000, 40000000);
    tree->SearchOrigin(cloud[i].position, callback1);
    tree->Search(cloud[i].position, callback2);
    ASSERT_EQ(1000, callback1.size());
    ASSERT_EQ(1000, callback2.size());

    auto it1 = callback1.result().begin();
    auto it2 = callback2.result().begin();
    // skip last 10 as UB
    for (size_t i = 0; i < 990; ++i) {
      EXPECT_EQ(*it1, *it2) << "#" << i << "; distance: " << it1->distance
                            << " vs " << it2->distance;
      ++it1;
      ++it2;
    }
  }
}

TEST(NanoflannWrapper, SearchVsSearch_0) {
  for (size_t i = 0; i < 64; ++i) {
    utils::nanoflann::tests::SearchCallback callback1(0, 30000);
    utils::nanoflann::tests::SearchCallback callback2(0, 30000);
    tree->SearchOrigin(cloud[i].position, callback1);
    tree->Search(cloud[i].position, callback2);

    EXPECT_EQ(callback1.size(), callback2.size());
    EXPECT_EQ(callback1.result(), callback2.result());
  }
}
