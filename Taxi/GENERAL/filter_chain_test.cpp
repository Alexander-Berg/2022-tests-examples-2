#include <gtest/gtest.h>

#include <candidates/filters/test/dummy.hpp>
#include <candidates/processors/utils/filter_chain.hpp>

namespace {

using candidates::processors::FilterChain;
namespace cf = candidates::filters;

std::vector<std::unique_ptr<cf::Filter>> MakeFilters() {
  static const cf::FilterInfo f1_info{"f1", {"f2"}, {}, false, {}};
  static const cf::FilterInfo f2_info{"f2", {"f3", "f4"}, {}, false, {}};
  static const cf::FilterInfo f3_info{"f3", {}, {}, false, {}};
  static const cf::FilterInfo f4_info{"f4", {"f3"}, {}, false, {}};
  static const cf::FilterInfo f5_info{"f5", {"f3"}, {"f6"}, false, {}};

  std::vector<std::unique_ptr<cf::Filter>> filters;

  // TODO: fix the wrong dependency order
  filters.push_back(std::make_unique<cf::test::AllowAll>(f1_info));
  filters.push_back(std::make_unique<cf::test::AllowAll>(f2_info));
  filters.push_back(std::make_unique<cf::test::AllowAll>(f3_info));
  filters.push_back(std::make_unique<cf::test::AllowAll>(f4_info));
  filters.push_back(std::make_unique<cf::test::AllowAll>(f5_info));

  return filters;
}

}  // namespace

TEST(FilterChain, Empty) {
  FilterChain c({});
  EXPECT_EQ(c.size(), 0);
}

TEST(FilterChain, Sample) {
  FilterChain chain(MakeFilters());

  ASSERT_EQ(chain.size(), 5);
  EXPECT_EQ(chain.size(), chain.GetPrimary().size());
  EXPECT_TRUE(chain.GetSecondary().empty());

  EXPECT_EQ(chain.Get(0).name(), "f1");
  EXPECT_EQ(chain.Get(1).name(), "f2");
  EXPECT_EQ(chain.Get(2).name(), "f3");
  EXPECT_EQ(chain.Get(3).name(), "f4");
  EXPECT_EQ(chain.Get(4).name(), "f5");

  EXPECT_EQ(chain.GetDependencies(0), std::vector<size_t>({1}));
  EXPECT_EQ(chain.GetDependencies(1), std::vector<size_t>({2, 3}));
  EXPECT_EQ(chain.GetDependencies(2), std::vector<size_t>());
  EXPECT_EQ(chain.GetDependencies(3), std::vector<size_t>({2}));
  EXPECT_EQ(chain.GetDependencies(4), std::vector<size_t>({2}));
}

TEST(FilterChain, Split) {
  FilterChain chain(MakeFilters());

  chain.Split({});
  EXPECT_EQ(chain.size(), chain.GetPrimary().size());
  EXPECT_TRUE(chain.GetSecondary().empty());

  chain.Split({"unknown"});
  EXPECT_EQ(chain.size(), chain.GetPrimary().size());
  EXPECT_TRUE(chain.GetSecondary().empty());

  chain.Split({"f5"});
  EXPECT_EQ(chain.size() - 1, chain.GetPrimary().size());
  EXPECT_EQ(1lu, chain.GetSecondary().size());

  chain.Split({"f3"});
  EXPECT_EQ(chain.size() - 3, chain.GetPrimary().size());
  EXPECT_EQ(3lu, chain.GetSecondary().size());
}
