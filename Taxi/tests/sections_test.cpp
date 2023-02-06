#include <iostream>
#include <optional>
#include <userver/utest/utest.hpp>

#include <taxi_config/taxi_config.hpp>
#include <testing/taxi_config.hpp>
#include <userver/formats/json.hpp>

#include <components/buttons.hpp>
#include <components/sections/build_sections.hpp>
#include <models/context.hpp>
#include <models/entrypoints.hpp>
#include <utils/metrics.hpp>
#include <variant>
#include "components/blocks.hpp"
#include "defs/api/api.hpp"
#include "fixtures.hpp"
#include "userver/utils/assert.hpp"

namespace fixtures {
std::optional<handlers::Shortcuts> BuildRequestShortcutsObj() {
  const auto supported_sections = std::vector<handlers::SupportedSection>(
      {{handlers::SectionType::kItemsLinearGrid},
       {handlers::SectionType::kButtonsContainer},
       {handlers::SectionType::kHeaderLinearGrid}});
  handlers::Shortcuts request_shortcuts_obj;
  request_shortcuts_obj.supported_sections =
      std::make_optional(supported_sections);
  return std::make_optional(request_shortcuts_obj);
}
}  // namespace fixtures

std::optional<std::vector<std::string>> merge_opt_vector(
    const std::optional<std::vector<std::string>>& first,
    const std::optional<std::vector<std::string>>& second) {
  if (!first) return second;
  if (!second) return first;
  std::vector<std::string> result;
  result.reserve(first->size() + second->size());
  std::merge(first->begin(), first->end(), second->begin(), second->end(),
             std::back_inserter(result));
  return result;
}

TEST(TestSectionsTagToPrevious, SingleSection) {
  // Make sure tags_to_previous works if there is only one section
  auto blocks = fixtures::BuildFakeBlocks(1);
  auto tags = std::make_optional(std::vector<std::string>{{"my_tag"}});
  auto previous_tags =
      std::make_optional(std::vector<std::string>{"previous_tag"});
  blocks[0].SetTags(tags, previous_tags);
  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      std::nullopt,  // header
      std::nullopt,  // buttons
      blocks, fixtures::BuildExperimentBasedParameters({}, std::nullopt));
  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), 1);
  auto section = std::get<handlers::ShortcutsSectionObject>(result[0]);
  EXPECT_EQ(section.tags, tags);
}

TEST(TestSectionsTagToPrevious, TwoItemsSections) {
  // Make sure tags_to_previous works if there are two shortcuts sections
  const int block_amount = 2;
  auto blocks = fixtures::BuildFakeBlocks(block_amount);
  auto tags = std::make_optional(std::vector<std::string>{"my_tag"});
  auto previous_tags =
      std::make_optional(std::vector<std::string>{"previous_tag"});
  auto& second_block = blocks[1];
  second_block.SetTags(tags, previous_tags);
  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      std::nullopt,  // header
      std::nullopt,  // buttons
      blocks, fixtures::BuildExperimentBasedParameters({}, std::nullopt));
  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), block_amount);
  auto first_section = std::get<handlers::ShortcutsSectionObject>(result[0]);
  auto second_section = std::get<handlers::ShortcutsSectionObject>(result[1]);
  EXPECT_EQ(first_section.tags, previous_tags);
  EXPECT_EQ(second_section.tags, tags);
}

TEST(TestSectionsTagToPrevious, OrderedSections) {
  const int block_amount = 3;
  auto blocks = fixtures::BuildFakeBlocks(block_amount);
  auto section_a_tags = std::make_optional(std::vector<std::string>{"aaa"});
  auto section_b_tags = std::make_optional(std::vector<std::string>{"bbb"});
  auto section_c_tags = std::make_optional(std::vector<std::string>{"ccc"});

  blocks[0].SetTags(section_a_tags, std::nullopt);
  blocks[1].SetTags(section_b_tags, std::nullopt);
  blocks[2].SetTags(section_c_tags, std::nullopt);

  std::vector<std::string> order{"slug_2", "slug_0", "slug_1"};
  e3c::ShortcutsSectionsSettings::Value sections_settings{order};

  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      std::nullopt,  // header
      std::nullopt,  // buttons
      blocks, fixtures::BuildExperimentBasedParameters({}, sections_settings));

  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), block_amount);
  auto first_section = std::get<handlers::ShortcutsSectionObject>(result[0]);
  auto second_section = std::get<handlers::ShortcutsSectionObject>(result[1]);
  auto third_section = std::get<handlers::ShortcutsSectionObject>(result[2]);
  EXPECT_EQ(first_section.tags, section_c_tags);
  EXPECT_EQ(second_section.tags, section_a_tags);
  EXPECT_EQ(third_section.tags, section_b_tags);
}

TEST(TestSectionsTagToPrevious, OrderedSectionsWithPrevious) {
  const int block_amount = 3;
  auto blocks = fixtures::BuildFakeBlocks(block_amount);
  auto section_a_tags = std::make_optional(std::vector<std::string>{"aaa"});
  auto section_b_tags = std::make_optional(std::vector<std::string>{"bbb"});
  auto section_c_tags = std::make_optional(std::vector<std::string>{"ccc"});
  auto previous_tags_from_b =
      std::make_optional(std::vector<std::string>{"previous_tag_from_b"});

  blocks[0].SetTags(section_a_tags, std::nullopt);
  blocks[1].SetTags(section_b_tags, previous_tags_from_b);
  blocks[2].SetTags(section_c_tags, std::nullopt);

  std::vector<std::string> order{"slug_2", "slug_1", "slug_0"};
  e3c::ShortcutsSectionsSettings::Value sections_settings{order};

  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      std::nullopt,  // header
      std::nullopt,  // buttons
      blocks, fixtures::BuildExperimentBasedParameters({}, sections_settings));

  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), block_amount);

  auto first_section = std::get<handlers::ShortcutsSectionObject>(result[0]);
  auto second_section = std::get<handlers::ShortcutsSectionObject>(result[1]);
  auto third_section = std::get<handlers::ShortcutsSectionObject>(result[2]);

  auto expected_tags_for_first_section =
      merge_opt_vector(section_c_tags, previous_tags_from_b);

  EXPECT_EQ(first_section.tags, expected_tags_for_first_section);
  EXPECT_EQ(second_section.tags, section_b_tags);
  EXPECT_EQ(third_section.tags, section_a_tags);
}

TEST(TestSectionsTagToPrevious, OrderedSectionsWithPreviousToBricks) {
  const int block_amount = 2;
  auto blocks = fixtures::BuildFakeBlocks(block_amount);
  auto previous_tags_from_header =
      std::make_optional(std::vector<std::string>{"previous_tag_from_header"});
  auto previous_tags_from_b =
      std::make_optional(std::vector<std::string>{"previous_tag_from_b"});

  blocks[1].SetTags(std::nullopt, previous_tags_from_b);

  std::vector<std::string> order{"slug_0", "header", "slug_1"};
  e3c::ShortcutsSectionsSettings::Value sections_settings{order};

  auto bricks = fixtures::BuildFakeOfferItems();
  shortcuts::experiments::BlocksMap blocks_map;
  blocks_map.blocks.insert(
      {"header", fixtures::BuildBlockAppearance(std::nullopt,
                                                previous_tags_from_header)});
  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      bricks,        // header
      std::nullopt,  // buttons
      blocks,
      fixtures::BuildExperimentBasedParameters(blocks_map, sections_settings));

  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), 3);
  auto first_section = std::get<handlers::ShortcutsSectionObject>(result[0]);
  auto second_section = std::get<handlers::ShortcutsSectionObject>(result[1]);
  EXPECT_EQ(first_section.tags, previous_tags_from_header);
  EXPECT_EQ(second_section.tags, previous_tags_from_b);
}

TEST(TestSectionsTagToPrevious, PreviousIsBrick) {
  // Make sure tags_to_previous works if previous is brick section
  auto blocks = fixtures::BuildFakeBlocks(1);
  auto tags = std::make_optional(std::vector<std::string>{"my_tag"});
  auto previous_tags =
      std::make_optional(std::vector<std::string>{"previous_tag"});
  blocks[0].SetTags(tags, previous_tags);
  auto bricks = fixtures::BuildFakeOfferItems();
  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      bricks,        // header
      std::nullopt,  // buttons
      blocks, fixtures::BuildExperimentBasedParameters({}, std::nullopt));
  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), 2);
  auto first_section = std::get<handlers::ShortcutsSectionObject>(result[0]);
  auto second_section = std::get<handlers::ShortcutsSectionObject>(result[1]);
  EXPECT_EQ(first_section.tags, previous_tags);
  EXPECT_EQ(second_section.tags, tags);
}

TEST(TestSectionsTagToPrevious, PreviousIsButton) {
  // Make sure tags_to_previous works if previous is buttons section
  auto blocks = fixtures::BuildFakeBlocks(1);
  auto tags = std::make_optional(std::vector<std::string>{"my_tag"});
  auto previous_tags =
      std::make_optional(std::vector<std::string>{"previous_tag"});
  blocks[0].SetTags(tags, previous_tags);
  auto buttons = fixtures::BuildFakeButtons();
  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      std::nullopt,  // header
      buttons,       // buttons
      blocks, fixtures::BuildExperimentBasedParameters({}, std::nullopt));
  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), 2);
  auto first_section = std::get<handlers::ButtonsSectionObject>(result[0]);
  auto second_section = std::get<handlers::ShortcutsSectionObject>(result[1]);
  EXPECT_EQ(first_section.tags, previous_tags);
  EXPECT_EQ(second_section.tags, tags);
}

TEST(TestShop, TestWithButtons) {
  // Make sure tags_to_previous works if previous is buttons section
  auto blocks = fixtures::BuildFakeBlocks(1);
  auto buttons = fixtures::BuildFakeButtons();
  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      std::nullopt,  // header
      buttons,       // buttons
      blocks, fixtures::BuildExperimentBasedParameters({}, std::nullopt));
  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), 2);
}

TEST(TestShop, TestWithoutButtons) {
  // Make sure tags_to_previous works if previous is buttons section
  auto blocks = fixtures::BuildFakeBlocks(1);
  auto result_opt = shortcuts::sections::BuildSections(
      fixtures::BuildRequestShortcutsObj(),
      std::nullopt,  // header
      std::nullopt,  // buttons
      blocks, fixtures::BuildExperimentBasedParameters({}, std::nullopt));
  EXPECT_TRUE(result_opt.has_value());
  auto result = *result_opt;
  EXPECT_EQ(result.size(), 1);
}
