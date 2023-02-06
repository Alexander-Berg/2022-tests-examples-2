#include <gtest/gtest.h>

#include <string>

#include <ml/common/filesystem.hpp>
#include <ml/common/json.hpp>
#include <ml/eats/retail/suggest/v1/resource.hpp>
#include <ml/eats/retail/suggest/v1/resources/objects.hpp>

#include "common/utils.hpp"

namespace {
namespace suggest = ml::eats::retail::suggest;
namespace v1 = suggest::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("eats/retail/suggest");
}  // namespace

TEST(Parse, ComplementProduct) {
  const v1::resources::ComplementProduct expected{
      "test_public_id",  // public_id
      123.456,           // npmi
  };

  const auto kJson = R"({"public_id":"test_public_id","npmi":123.456})";
  const auto actual =
      ml::common::FromJsonString<v1::resources::ComplementProduct>(kJson);

  ASSERT_EQ(expected, actual);
}

TEST(Parse, ProductNoComplements) {
  const v1::resources::Product expected{
      "test_public_id",  // public_id
      1,                 // brand_id
      {},                // complements
      5.0,               // price
      10,                // total_num_orders
      "для собак"        // category_name
  };

  const auto kJson =
      R"({"public_id":"test_public_id","brand_id":1,"complements":[],"price":5.0,"total_num_orders":10,"category_name":"для собак"})";
  const auto actual = ml::common::FromJsonString<v1::resources::Product>(kJson);

  ASSERT_TRUE(actual.complements.empty());
  ASSERT_EQ(expected, actual);
}

TEST(Parse, Product) {
  const v1::resources::Product expected{
      "test_public_id",  // public_id
      1,                 // brand_id
      {
          {
              "public_1",  // public_id
              123,         // npmi
          },
          {
              "public_2",  // public_id
              456,         // npmi
          },
          {
              "public_3",  // public_id
              789,         // npmi
          },
      },           // complements
      5.0,         // price
      10,          // total_num_orders
      "для собак"  // category_name
  };

  const auto kJson =
      R"({"public_id":"test_public_id","brand_id":1,"complements":[
        {"public_id":"public_1","npmi": 123},
        {"public_id":"public_2","npmi": 456},
        {"public_id":"public_3","npmi": 789}
      ],"price":5.0,"total_num_orders":10,"category_name":"для собак"})";
  const auto actual = ml::common::FromJsonString<v1::resources::Product>(kJson);

  ASSERT_FALSE(actual.complements.empty());
  ASSERT_EQ(expected, actual);
}

TEST(LoadResourceFromDir, EmptyResource) {
  v1::Resource resource;
  ASSERT_NO_THROW(resource = v1::LoadResourceFromDir(kTestDataDir,
                                                     "empty_resource.txt",
                                                     "empty_resource.txt"));

  ASSERT_TRUE(resource.IsEmpty());
  ASSERT_TRUE(resource.IsFallbackEmpty());
}

TEST(LoadResourceFromDir, Simple) {
  v1::Resource resource;
  ASSERT_NO_THROW(resource = v1::LoadResourceFromDir(kTestDataDir, "simple.txt",
                                                     "simple_fallback.txt"));

  ASSERT_FALSE(resource.IsEmpty());
  ASSERT_FALSE(resource.IsFallbackEmpty());

  {
    const auto product_opt = resource.GetProduct(suggest::PublicId{"public_1"});
    ASSERT_TRUE(product_opt.has_value());
    ASSERT_TRUE(product_opt->complements.empty());
  }

  {
    const auto product_opt = resource.GetProduct(suggest::PublicId{"public_2"});
    ASSERT_TRUE(product_opt.has_value());
    ASSERT_FALSE(product_opt->complements.empty());
    ASSERT_EQ(product_opt->complements.size(), 1ul);
  }
  {
    const auto product_opt = resource.GetFallbackProduct(suggest::BrandId{1});
    ASSERT_TRUE(product_opt.has_value());
    ASSERT_TRUE(product_opt->complements.empty());
  }
  {
    const auto product_opt = resource.GetFallbackProduct(suggest::BrandId{2});
    ASSERT_TRUE(product_opt.has_value());
    ASSERT_FALSE(product_opt->complements.empty());
    ASSERT_EQ(product_opt->complements.size(), 1ul);
  }
}

TEST(Parse, FallbackProduct) {
  const v1::resources::FallbackProduct expected{
      "test_public_id",  // public_id
  };

  const auto kJson = R"({"public_id":"test_public_id"})";
  const auto actual =
      ml::common::FromJsonString<v1::resources::FallbackProduct>(kJson);

  ASSERT_EQ(expected, actual);
}

TEST(Parse, BrandFallbackProducts) {
  std::vector<v1::resources::FallbackProduct> prod;
  prod.push_back(v1::resources::FallbackProduct{"public_1"});
  prod.push_back(v1::resources::FallbackProduct{"public_2"});
  prod.push_back(v1::resources::FallbackProduct{"public_3"});
  const v1::resources::BrandFallbackProducts expected{
      0,     // brand_id
      prod,  // complements
  };

  const auto kJson =
      R"({"brand_id":0,"complements":[
        {"public_id":"public_1"},
        {"public_id":"public_2"},
        {"public_id":"public_3"}
      ]})";
  const auto actual =
      ml::common::FromJsonString<v1::resources::BrandFallbackProducts>(kJson);

  ASSERT_FALSE(actual.complements.value().empty());
  ASSERT_EQ(expected, actual);
}
