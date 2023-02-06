#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/tags_exclusion.hpp>

TEST(TestTagsExclusion, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& tags_exclusion_config = config.Get<config::TagsExclusion>();

  const tags::models::BlockingTags& blocking_tags =
      tags_exclusion_config.Get(boost::none);
  ASSERT_TRUE(blocking_tags.IsEmpty());
}

TEST(TestTagsExclusion, Parse) {
  config::DocsMap docs_map = config::DocsMapForTest();

  docs_map.Override(
      "SEARCH_SETTINGS_CLASSES",
      BSON("__default__" << BSON(
               "__default__"
               << BSON("DISPATCH_DRIVER_TAGS_BLOCK" << BSON_ARRAY("bad_driver"
                                                                  << "bad_car"))
               << "econom"
               << BSON("DISPATCH_DRIVER_TAGS_BLOCK"
                       << BSON_ARRAY("econom_excluded")))));

  const auto& config = config::Config(docs_map);
  const auto& tags_exclusion_config = config.Get<config::TagsExclusion>();

  const tags::models::BlockingTags& blocking_tags =
      tags_exclusion_config.Get(boost::none);
  ASSERT_FALSE(blocking_tags.IsEmpty());

  const models::Classes econom{"econom"};
  ASSERT_TRUE(blocking_tags.Filter({"econom_excluded"}, econom).Empty());
  ASSERT_TRUE(blocking_tags.Filter({"vip"}, econom) == econom);

  const models::Classes vip{"comfort", "business", "vip"};
  ASSERT_TRUE(blocking_tags.Filter({"econom_excluded"}, vip) == vip);
  ASSERT_TRUE(blocking_tags.Filter({"bad_driver", "random_tag"}, vip).Empty());
  ASSERT_TRUE(blocking_tags.Filter({"bad_car"}, vip).Empty());
}
