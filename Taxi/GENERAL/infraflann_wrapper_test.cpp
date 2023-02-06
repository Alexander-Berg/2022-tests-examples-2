#include <gtest/gtest.h>

#include "infraflann_wrapper_utils.hpp"
#include "nanoflann/nanoflann_wrapper_utils.hpp"

namespace {

TEST(InfraflannSearch, SearchInfraVsSearch) {
  for (size_t i = 0; i < 50; ++i) {
    auto cloud = utils::infraflann::tests::GetCloud();
    auto tree1 =
        std::make_unique<utils::infraflann::tests::KDTree>(std::move(cloud));
    utils::infraflann::tests::SearchCallback callback1(tree1->GetPoints(), 1000,
                                                       40000000);
    tree1->BuildIndex();

    auto cloud_ = utils::nanoflann::tests::GetCloud();
    auto tree2 = std::make_unique<utils::nanoflann::tests::KDTree>(cloud_);
    utils::nanoflann::tests::SearchCallback callback2(1000, 40000000);
    tree2->BuildIndex();

    tree1->Search(cloud_[i].position, callback1);
    tree2->Search(cloud_[i].position, callback2);
    ASSERT_EQ(1000, callback1.size());
    ASSERT_EQ(1000, callback2.size());

    auto it1 = callback1.result().begin();
    auto it2 = callback2.result().begin();
    // skip last 10 as UB
    for (size_t i = 0; i < 990; ++i) {
      EXPECT_EQ(it1->distance, it2->distance)
          << "#" << i << "; distance: " << it1->distance << " vs "
          << it2->distance;
      ++it1;
      ++it2;
    }
  }
}

}  // namespace
