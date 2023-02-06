#include <gtest/gtest.h>

#include <candidates/configs/filters.hpp>
#include <candidates/filters/meta_factory.hpp>
#include <candidates/filters/self_diagnostics.hpp>
#include <candidates/filters/test/dummy.hpp>

using FiltersConfigs = candidates::configs::Filters;
using FilterConfig = candidates::models::FilterConfig;
namespace cf = candidates::filters;

namespace {

auto CreateFactory(const cf::FilterInfo& info) {
  return std::make_shared<cf::test::DummyFactory<cf::test::AllowAll>>(info);
}

}  // namespace

TEST(FiltersConfigs, Chains) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}, 1, 1, 1, {"tag1"}};
  cf::FilterInfo f2_info{"f2", {}, {}, false, {}, 1, 1, 1, {"tag1"}};
  cf::FilterInfo f3_info{"f3", {}, {}, false, {}, 1, 1, 1, {"tag2"}};
  cf::MetaFactory f(
      {CreateFactory(f1_info), CreateFactory(f2_info), CreateFactory(f3_info)},
      []() { return cf::SelfDiagnosticsData{}; }, stats);
  {
    FiltersConfigs configs(f, {});
    auto chain = configs.GetChain("tag1");
    ASSERT_EQ(chain.size(), 2);
    EXPECT_EQ(chain[0], "f1");
    EXPECT_EQ(chain[1], "f2");
    chain = configs.GetChain("tag2");
    ASSERT_EQ(chain.size(), 1);
    EXPECT_EQ(chain[0], "f3");
  }
  {
    FilterConfig f2_config;
    f2_config.tags = std::vector<std::string>{"tag3"};
    FiltersConfigs configs(f, {{"f2", f2_config}});
    auto chain = configs.GetChain("tag1");
    ASSERT_EQ(chain.size(), 1);
    EXPECT_EQ(chain[0], "f1");
    chain = configs.GetChain("tag2");
    ASSERT_EQ(chain.size(), 1);
    EXPECT_EQ(chain[0], "f3");
    chain = configs.GetChain("tag3");
    ASSERT_EQ(chain.size(), 1);
    EXPECT_EQ(chain[0], "f2");
  }
  {
    FilterConfig f2_config;
    FiltersConfigs configs(f, {{"f2", f2_config}});
    auto chain = configs.GetChain("tag1");
    ASSERT_EQ(chain.size(), 2);
    EXPECT_EQ(chain[0], "f1");
    EXPECT_EQ(chain[1], "f2");
    chain = configs.GetChain("tag2");
    ASSERT_EQ(chain.size(), 1);
    EXPECT_EQ(chain[0], "f3");
  }
  {
    FilterConfig f2_config;
    f2_config.tags = std::vector<std::string>{};
    FiltersConfigs configs(f, {{"f2", f2_config}});
    auto chain = configs.GetChain("tag1");
    ASSERT_EQ(chain.size(), 1);
    EXPECT_EQ(chain[0], "f1");
    chain = configs.GetChain("tag2");
    ASSERT_EQ(chain.size(), 1);
    EXPECT_EQ(chain[0], "f3");
  }
}
