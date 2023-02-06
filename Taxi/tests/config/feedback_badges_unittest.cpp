#include "config/feedbackbadges_config.hpp"
#include "utils/jsonfixtures.hpp"

#include <gtest/gtest.h>
#include <json/json.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/feedbackbadges_config.hpp>

TEST(TestFeedbackBadgesConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::FeedbackBadgesMapping& feedback_badges_config =
      config.Get<config::FeedbackBadgesMapping>();

  ASSERT_EQ(feedback_badges_config.badges.size(), 0u);
  ASSERT_EQ(feedback_badges_config.badges_rating_mapping.size(), 0u);
}

TEST(TestFeedbackBadgesConfig, StandardParsingConfig) {
  const auto& badges_mapping_bson =
      JSONFixtures::GetFixtureBSON("feedback_badges_standard_parse.json");
  config::FeedbackBadgesMapping feedback_badges_config;
  config::ParseFeedbackBadgesMapping(
      badges_mapping_bson["FEEDBACK_BADGES_MAPPING"], feedback_badges_config);

  ASSERT_EQ(feedback_badges_config.badges.size(), 6u);
  ASSERT_EQ(feedback_badges_config.badges_rating_mapping.size(), 5u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(5u).rating_badges.size(),
      3u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(4u).rating_badges.size(),
      3u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(3u).rating_badges.size(),
      1u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(2u).rating_badges.size(),
      1u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(1u).rating_badges.size(),
      3u);

  ASSERT_EQ(feedback_badges_config.badges.count("neatdriving"), 1u);
  ASSERT_EQ(feedback_badges_config.badges.at("neatdriving").name,
            "neatdriving");
  ASSERT_EQ(feedback_badges_config.badges.at("neatdriving").label,
            "feedback_badges.neatdriving");
  ASSERT_EQ(feedback_badges_config.badges.at("neatdriving").active_image_tag,
            "tag.neatdriving");
  ASSERT_EQ(feedback_badges_config.badges.at("neatdriving").inactive_image_tag,
            "tag.inneatdriving");
  ASSERT_EQ(feedback_badges_config.badges.at("neatdriving")
                .filters.tariffs.count("vip"),
            1u);
  ASSERT_EQ(feedback_badges_config.badges.at("neatdriving").filters.notrip,
            true);
  ASSERT_EQ(feedback_badges_config.badges.at("neatdriving").filters.cash,
            false);

  ASSERT_EQ(feedback_badges_config.badges.count("care"), 1u);
  ASSERT_EQ(feedback_badges_config.badges.at("care").name, "care");
  ASSERT_EQ(feedback_badges_config.badges.at("care").label,
            "feedback_badges.care");
  ASSERT_EQ(feedback_badges_config.badges.at("care").active_image_tag, "");
  ASSERT_EQ(feedback_badges_config.badges.at("care").inactive_image_tag, "");
  ASSERT_EQ(
      feedback_badges_config.badges.at("care").filters.tariffs.count("default"),
      1u);
  ASSERT_EQ(feedback_badges_config.badges.at("care").filters.notrip, false);
  ASSERT_EQ(feedback_badges_config.badges.at("care").filters.cash, false);

  ASSERT_EQ(
      feedback_badges_config.badges.at("pleasantmusic").filters.tariffs.size(),
      2u);
  ASSERT_EQ(
      feedback_badges_config.badges.at("comfortatmosphere").filters.notrip,
      false);
  ASSERT_EQ(feedback_badges_config.badges.at("comfortatmosphere").filters.cash,
            true);
}

TEST(TestFeedbackBadgesConfig, EmptyParsingConfig) {
  const auto& badges_mapping_bson =
      JSONFixtures::GetFixtureBSON("feedback_badges_empty_parse.json");
  config::FeedbackBadgesMapping feedback_badges_config;
  config::ParseFeedbackBadgesMapping(
      badges_mapping_bson["FEEDBACK_BADGES_MAPPING"], feedback_badges_config);

  ASSERT_EQ(feedback_badges_config.badges.size(), 0u);
  ASSERT_EQ(feedback_badges_config.badges_rating_mapping.size(), 0u);
}

TEST(TestFeedbackBadgesConfig, ErrorsInBadgesParsingConfig) {
  const auto& badges_mapping_bson =
      JSONFixtures::GetFixtureBSON("feedback_badges_error_badges_parse.json");
  config::FeedbackBadgesMapping feedback_badges_config;
  config::ParseFeedbackBadgesMapping(
      badges_mapping_bson["FEEDBACK_BADGES_MAPPING"], feedback_badges_config);

  ASSERT_EQ(feedback_badges_config.badges.size(), 2u);

  ASSERT_EQ(feedback_badges_config.badges.at("goodcar").label,
            "feedback_badges.goodcar");
  ASSERT_EQ(feedback_badges_config.badges.at("goodcar").active_image_tag,
            "tag.goodcar");
  ASSERT_EQ(feedback_badges_config.badges.at("goodcar").inactive_image_tag,
            "tag.ingoodcar");

  ASSERT_EQ(feedback_badges_config.badges.at("care").label,
            "feedback_badges.care");
  ASSERT_EQ(feedback_badges_config.badges.at("care").active_image_tag, "");
  ASSERT_EQ(feedback_badges_config.badges.at("care").inactive_image_tag, "");
}

TEST(TestFeedbackBadgesConfig, UnwantedBadgesInRatings) {
  const auto& badges_mapping_bson = JSONFixtures::GetFixtureBSON(
      "feedback_badges_unwanted_badges_parse.json");
  config::FeedbackBadgesMapping feedback_badges_config;
  config::ParseFeedbackBadgesMapping(
      badges_mapping_bson["FEEDBACK_BADGES_MAPPING"], feedback_badges_config);

  ASSERT_EQ(feedback_badges_config.badges.size(), 1u);
  ASSERT_EQ(feedback_badges_config.badges_rating_mapping.size(), 5u);

  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(1u).rating_badges.size(),
      0u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(2u).rating_badges.size(),
      1u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(3u).rating_badges.size(),
      0u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(4u).rating_badges.size(),
      1u);
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(5u).rating_badges.size(),
      1u);
}

TEST(TestFeedbackBadgesConfig, ErrorsInRatings) {
  const auto& badges_mapping_bson =
      JSONFixtures::GetFixtureBSON("feedback_badges_error_rating_parse.json");
  config::FeedbackBadgesMapping feedback_badges_config;
  config::ParseFeedbackBadgesMapping(
      badges_mapping_bson["FEEDBACK_BADGES_MAPPING"], feedback_badges_config);

  ASSERT_EQ(feedback_badges_config.badges.size(), 6u);
  ASSERT_EQ(feedback_badges_config.badges_rating_mapping.size(), 3u);

  ASSERT_EQ(feedback_badges_config.badges_rating_mapping.count(1u), 0u);

  ASSERT_EQ(feedback_badges_config.badges_rating_mapping.at(4u).choice_title,
            "");
  ASSERT_EQ(
      feedback_badges_config.badges_rating_mapping.at(4u).rating_badges.size(),
      3u);
}
