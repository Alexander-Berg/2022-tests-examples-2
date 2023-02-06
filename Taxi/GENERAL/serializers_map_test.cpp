#include <gtest/gtest.h>

#include "serializers_map.hpp"

using candidates::filters::Context;
using candidates::filters::Serializer;
using candidates::filters::SerializerException;
using candidates::filters::SerializersMap;

namespace {

class SampleSerializer : public Serializer {
 public:
  SampleSerializer() : Serializer("sample", "test/sample") {}

  formats::json::Value Serialize([
      [maybe_unused]] const Context& context) const override {
    return {};
  }
};

}  // namespace

TEST(SerializerMap, Empty) {
  SerializersMap map({});
  EXPECT_NO_THROW(map.Get({"some", "names"}).empty());
  EXPECT_TRUE(map.Get({"some", "names"}).empty());
}

TEST(SerializerManager, AlreadyRegistered) {
  EXPECT_THROW(SerializersMap({std::make_shared<SampleSerializer>(),
                               std::make_shared<SampleSerializer>()}),
               SerializerException);
}

TEST(SerializerManager, Sample) {
  SerializersMap map({std::make_shared<SampleSerializer>()});
  const auto& serializers = map.Get({"sample"});
  ASSERT_EQ(serializers.size(), 1);
  EXPECT_EQ(serializers[0]->name(), "sample");
}
