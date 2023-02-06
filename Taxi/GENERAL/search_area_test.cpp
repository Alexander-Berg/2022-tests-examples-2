#include <gtest/gtest.h>

#include <filters/infrastructure/search_area/search_area.hpp>

namespace cf = candidates::filters;
namespace cfi = candidates::filters::infrastructure;

namespace {

const cf::FilterInfo kEmptyInfo;

models::geometry::Polygon MakeSearchArea() {
  return models::geometry::Polygon({
      {37.309394, 55.914744},
      {37.884803, 55.911659},
      {37.942481, 55.520175},
      {37.242102, 55.499913},
      {37.309394, 55.914744},
  });
}

}  // namespace

TEST(SearchArea, Sample) {
  const auto& search_area = MakeSearchArea();
  cfi::SearchArea filter(kEmptyInfo, search_area);
  cf::Context context;

  // Not inside search area
  EXPECT_EQ(filter.Process({{37.093787, 55.914744}, "id"}, context),
            cf::Result::kDisallow);
  // Ok
  EXPECT_EQ(filter.Process({{37.584052, 55.805071}, "id"}, context),
            cf::Result::kAllow);
}
