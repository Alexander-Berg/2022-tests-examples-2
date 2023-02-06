#include <data_provider/adaptor.hpp>

#include <gtest/gtest.h>

namespace {

class TestCache {
 public:
  auto Get() const { return std::make_shared<std::string>("Hello World!"); }
};

}  // namespace

TEST(DataProvider, Adaptor) {
  using StrAdaptor = data_provider::Adaptor<std::string>;
  TestCache cache;

  StrAdaptor adaptor0(cache);
  const auto& value0 = adaptor0.Get();
  EXPECT_FALSE(value0->empty());

  StrAdaptor adaptor1(cache, &TestCache::Get);
  const auto& value1 = adaptor1.Get();
  EXPECT_FALSE(value1->empty());
}
