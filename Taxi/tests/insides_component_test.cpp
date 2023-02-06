#include <components/dashboard_insides_component.hpp>
#include <userver/utest/utest.hpp>
#include <vector>

namespace eats_report_storage::testing {

using types::Inside;
using types::InsideList;
using types::InsideSlug;

using ConfigInside = taxi_config::eats_report_storage_insides_config::Inside;
using ConfigInsideList = std::vector<ConfigInside>;

static constexpr size_t kInsidesDatasetSize{3};

using components::DashboardInsidesComponentImpl;

ConfigInsideList MakeInsides(size_t count) {
  ConfigInsideList insides;
  insides.reserve(count);
  for (size_t i = 0; i < count; ++i) {
    insides.push_back(
        {"inside_" + std::to_string(i), "icon_" + std::to_string(i),
         "title_" + std::to_string(i), "description_" + std::to_string(i)});
  }
  return insides;
}

TEST(CheckInsidesImpl, empty_filters) {
  std::vector<InsideSlug> filter = {};
  auto insides = MakeInsides(kInsidesDatasetSize);

  DashboardInsidesComponentImpl impl;
  auto filtered_insides = impl.GetFilteredInsides(insides, filter);

  ASSERT_EQ(filtered_insides.size(), insides.size());
  ASSERT_EQ(filtered_insides[0].icon_slug, "icon_0");
  ASSERT_EQ(filtered_insides[1].icon_slug, "icon_1");
}

TEST(CheckInsidesImpl, not_empty_filters) {
  std::vector<InsideSlug> filter = {"inside_0", "inside_2"};

  auto insides = MakeInsides(kInsidesDatasetSize);

  DashboardInsidesComponentImpl impl;
  auto filtered_insides = impl.GetFilteredInsides(insides, filter);

  ASSERT_EQ(filtered_insides.size(), 2);
  ASSERT_EQ(filtered_insides[0].icon_slug, "icon_0");
  ASSERT_EQ(filtered_insides[1].icon_slug, "icon_2");
}

TEST(CheckInsidesImpl, filter_with_trash) {
  std::vector<InsideSlug> filter = {"inside_0", "inside_2", "trash_slug"};

  auto insides = MakeInsides(kInsidesDatasetSize);

  DashboardInsidesComponentImpl impl;
  auto filtered_insides = impl.GetFilteredInsides(insides, filter);

  ASSERT_EQ(filtered_insides.size(), 2);
  ASSERT_EQ(filtered_insides[0].icon_slug, "icon_0");
  ASSERT_EQ(filtered_insides[1].icon_slug, "icon_2");
}

TEST(CheckInsidesImpl, check_order_and_trash_skip) {
  std::vector<InsideSlug> filter = {"inside_0", "inside_1", "trash",
                                    "inside_2"};

  auto insides = MakeInsides(kInsidesDatasetSize);

  DashboardInsidesComponentImpl impl;
  auto filtered_insides = impl.GetFilteredInsides(insides, filter);
  std::reverse(filter.begin(), filter.end());
  auto filtered_insides_reversed = impl.GetFilteredInsides(insides, filter);

  ASSERT_EQ(filtered_insides[0].icon_slug,
            filtered_insides_reversed[2].icon_slug);
}

}  // namespace eats_report_storage::testing
