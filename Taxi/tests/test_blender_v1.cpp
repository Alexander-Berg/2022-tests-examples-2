#include <gtest/gtest.h>

#include <ml/blender/v1/assignment/assignment.hpp>
#include <ml/blender/v1/layout.hpp>
#include <ml/common/filesystem.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::blender::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("blender_v1");

class ConstScorer : public strategies::assignment::IAssignmentScorer {
 public:
  explicit ConstScorer(std::string scenario, double value)
      : scenario_(std::move(scenario)), value_(value){};

  void UpdateCosts(ml::common::algo::AssignmentTask& task,
                   const strategies::assignment::ShortcutLocations&,
                   const strategies::assignment::ShortcutCandidates& candidates)
      const final {
    for (size_t row = 0; row < task.GetRowsCount(); ++row) {
      for (size_t column = 0; column < task.GetColumnsCount(); ++column) {
        if (candidates[column].shortcut_cref.get().scenario == scenario_) {
          task.At(row, column) += value_;
        }
      }
    }
  }

 private:
  const std::string scenario_;
  const double value_;
};

}  // namespace

TEST(BlenderV1, layout) {
  LayoutBuilder builder(6);
  ASSERT_EQ(builder.AddCell(4, 2), LayoutBuilder::Location({0, 0}));
  ASSERT_EQ(builder.AddCell(2, 2), LayoutBuilder::Location({0, 4}));
  ASSERT_EQ(builder.AddCell(2, 4), LayoutBuilder::Location({2, 0}));
  ASSERT_EQ(builder.AddCell(4, 2), LayoutBuilder::Location({2, 2}));
  ASSERT_EQ(builder.AddCell(4, 2), LayoutBuilder::Location({4, 2}));
  ASSERT_EQ(builder.AddCell(4, 4), LayoutBuilder::Location({6, 0}));
  ASSERT_EQ(builder.AddCell(2, 4), LayoutBuilder::Location({6, 4}));
  ASSERT_EQ(builder.AddCell(3, 3), LayoutBuilder::Location({10, 0}));
  ASSERT_EQ(builder.AddCell(3, 3), LayoutBuilder::Location({10, 3}));
  ASSERT_EQ(builder.AddCell(6, 1), LayoutBuilder::Location({13, 0}));
  ASSERT_EQ(builder.AddCell(1, 1), LayoutBuilder::Location({14, 0}));
  ASSERT_EQ(builder.AddCell(1, 1), LayoutBuilder::Location({14, 1}));
  builder.Reset();
  ASSERT_EQ(builder.AddCell(4, 2), LayoutBuilder::Location({0, 0}));
  ASSERT_EQ(builder.AddCell(2, 2), LayoutBuilder::Location({0, 4}));
  ASSERT_EQ(builder.AddCell(2, 4), LayoutBuilder::Location({2, 0}));
  ASSERT_EQ(builder.AddCell(4, 2), LayoutBuilder::Location({2, 2}));
  ASSERT_EQ(builder.AddCell(4, 2), LayoutBuilder::Location({4, 2}));
  builder.Reset();
  ASSERT_EQ(builder.AddCell(3, 2), LayoutBuilder::Location({0, 0}));
  ASSERT_EQ(builder.AddCell(3, 4), LayoutBuilder::Location({0, 3}));
  ASSERT_EQ(builder.AddCell(3, 2), LayoutBuilder::Location({2, 0}));
  builder.Reset();
  ASSERT_EQ(builder.AddCell(4, 2), LayoutBuilder::Location({0, 0}));
  ASSERT_EQ(builder.AddCell(2, 4), LayoutBuilder::Location({0, 4}));
  ASSERT_EQ(builder.AddCell(2, 2), LayoutBuilder::Location({2, 0}));
  ASSERT_EQ(builder.AddCell(2, 2), LayoutBuilder::Location({2, 2}));
}

TEST(BlenderV1, alignment) {
  using namespace strategies::assignment;
  ShortcutLocations locations;
  size_t locations_count{0};

  locations.push_back({0, 0, 4, 2, {}});
  locations.push_back({0, 4, 2, 2, {}});
  locations.push_back({2, 0, 3, 3, {}});
  locations.push_back({2, 3, 3, 3, {}});
  locations.push_back({4, 0, 2, 2, {}});
  locations.push_back({4, 2, 4, 2, {}});
  locations_count = locations.size();
  alignment::AlignLines(locations, locations_count);
  ASSERT_EQ(locations_count, locations.size());
  locations.clear();

  locations.push_back({0, 0, 3, 2, {}});
  locations.push_back({0, 3, 3, 4, {}});
  locations.push_back({2, 0, 3, 2, {}});
  locations_count = locations.size();
  alignment::AlignLines(locations, locations_count);
  ASSERT_EQ(locations_count, locations.size());
  locations.clear();

  locations.push_back({0, 0, 4, 2, {}});
  locations.push_back({0, 4, 2, 4, {}});
  locations.push_back({2, 0, 2, 2, {}});
  locations.push_back({2, 2, 2, 2, {}});
  locations_count = locations.size();
  alignment::AlignLines(locations, locations_count);
  ASSERT_EQ(locations_count, locations.size());
  locations.clear();

  locations.push_back({0, 0, 3, 2, {}});
  locations.push_back({0, 3, 3, 2, {}});
  locations.push_back({2, 0, 3, 2, {}});  // bad location
  locations_count = locations.size();
  alignment::AlignLines(locations, locations_count);
  ASSERT_EQ(locations_count, locations.size() - 1);
  locations.clear();

  locations.push_back({0, 0, 4, 2, {}});
  locations_count = locations.size();
  alignment::AlignLines(locations, locations_count);
  ASSERT_EQ(locations_count, locations.size() - 1);
  locations.clear();

  locations.push_back({0, 0, 4, 2, {}});
  locations.push_back({0, 4, 2, 2, {}});
  locations_count = 1;
  alignment::AlignLines(locations, locations_count);
  ASSERT_EQ(locations_count, 0ul);
  locations.clear();
}

TEST(BlenderV1, assignment) {
  using namespace strategies::assignment;

  auto state = ml::common::FromJsonString<State>(
      ml::common::ReadFileContents(kTestDataDir + "/simple_state.json"));

  AssignmentConfig config;
  config.max_top_taken = 10;
  config.line_damping_rate = 0.8;
  config.left_to_right_damping_rate = 0.95;
  config.max_lines_number = 3;
  config.layout_rule_backoff = 2;
  config.tag_shortcuts_extractor_config = {
      10,
      {},
      {},
      {{{"scenario1", {}, {}}, {"scenario2", {}, {2}}, {"scenario3", {}, {}}}}};
  config.scenario_configs.push_back({"scenario1", 1, 0.5, 0, 0});
  config.scenario_configs.push_back({"scenario2", 1, 0.5, 0, 0});
  config.scenario_configs.push_back({"scenario3", 1, 0.5, 0, 0});
  config.scenario_configs.push_back({"scenario4", 10, 0.5, 0, 0});
  config.scenario_title_cut_configs.push_back({"scenario1", 10, {}});
  config.scenario_title_cut_configs.push_back({"scenario2", 10, {}});
  config.scenario_title_cut_configs.push_back({"scenario3", 10, {}});
  config.skip_on_max_assignment = true;
  Assignment algo(config);

  ShortcutLocations locations;
  locations.push_back({0, 0, 4, 2, {{"loc_tag1"}}});
  locations.push_back({0, 4, 2, 2, {{"loc_tag1", "loc_tag2"}}});
  locations.push_back({2, 0, 3, 3, {{"loc_tag4", "loc_tag3"}}});
  locations.push_back({2, 3, 3, 3, {{"loc_tag1"}}});
  locations.push_back({4, 0, 2, 2, {{"loc_tag3"}}});
  locations.push_back({4, 2, 4, 2, {{"loc_tag2"}}});
  locations.push_back({6, 0, 5, 2, {{"loc_tag2"}}});  // bad location
  auto generator = std::make_shared<ConstantGenerator>(locations);
  algo.SetGenerator(generator);

  auto state1 = algo.Apply(State(state));

  ASSERT_EQ(state1.grid.cells.size(), 6ul);
  ASSERT_EQ(state1.grid.cells[0].shortcut.id, "scenario1#1");
  ASSERT_EQ(state1.grid.cells[1].shortcut.id, "scenario3#1");
  ASSERT_EQ(state1.grid.cells[2].shortcut.id, "scenario2#1");
  ASSERT_EQ(state1.grid.cells[3].shortcut.id, "scenario1#2");
  ASSERT_EQ(state1.grid.cells[4].shortcut.id, "scenario3#2");
  ASSERT_EQ(state1.grid.cells[5].shortcut.id, "scenario1#3");

  std::vector<TagMatchScorerConfig> scorer_configs1 = {
      {{}, "shortcut_tag1", "loc_tag3", 100}};
  algo.AddScorer(std::make_shared<TagMatchScorer>(scorer_configs1));

  auto state2 = algo.Apply(State(state));
  ASSERT_EQ(state2.grid.cells.size(), 6ul);
  ASSERT_EQ(state2.grid.cells[0].shortcut.id, "scenario1#1");
  ASSERT_EQ(state2.grid.cells[1].shortcut.id, "scenario3#1");
  ASSERT_EQ(state2.grid.cells[2].shortcut.id, "scenario2#2");
  ASSERT_EQ(state2.grid.cells[3].shortcut.id, "scenario2#1");
  ASSERT_EQ(state2.grid.cells[4].shortcut.id, "scenario3#2");
  ASSERT_EQ(state2.grid.cells[5].shortcut.id, "scenario1#2");

  std::vector<TagMatchScorerConfig> scorer_configs2 = {
      {{"scenario1"}, "shortcut_tag2", "loc_tag4", 100},
      {{"scenario3"}, "shortcut_tag2", "loc_tag4", 10000}};
  algo.AddScorer(std::make_shared<TagMatchScorer>(scorer_configs2));
  std::vector<TagUsageScorerConfig> scorer_configs3 = {
      {{}, "tag_scenario3#2", 0.1}};
  algo.AddScorer(std::make_shared<TagUsageScorer>(scorer_configs3));

  auto state3 = algo.Apply(State(state));
  ASSERT_EQ(state3.grid.cells.size(), 6ul);
  ASSERT_EQ(state3.grid.cells[0].shortcut.id, "scenario2#1");
  ASSERT_EQ(state3.grid.cells[1].shortcut.id, "scenario3#1");
  ASSERT_EQ(state3.grid.cells[2].shortcut.id, "scenario1#1");
  ASSERT_EQ(state3.grid.cells[3].shortcut.id, "scenario1#2");
  ASSERT_EQ(state3.grid.cells[4].shortcut.id, "scenario2#2");
  ASSERT_EQ(state3.grid.cells[5].shortcut.id, "scenario3#2");

  LocationDiscountScorerConfig config4{0.5, 1};
  algo.AddScorer(std::make_shared<LocationDiscountScorer>(config4));
  auto state4 = algo.Apply(State(state));
  ASSERT_EQ(state4.grid.cells.size(), 6ul);
  ASSERT_EQ(state4.grid.cells[0].shortcut.id, "scenario2#1");
  ASSERT_EQ(state4.grid.cells[1].shortcut.id, "scenario3#1");
  ASSERT_EQ(state4.grid.cells[2].shortcut.id, "scenario1#1");
  ASSERT_EQ(state4.grid.cells[3].shortcut.id, "scenario3#2");
  ASSERT_EQ(state4.grid.cells[4].shortcut.id, "scenario2#2");
  ASSERT_EQ(state4.grid.cells[5].shortcut.id, "scenario1#2");

  algo.AddScorer(std::make_shared<ConstScorer>(
      "scenario1", std::numeric_limits<double>::infinity()));
  algo.AddScorer(std::make_shared<ConstScorer>(
      "scenario2", std::numeric_limits<double>::infinity()));
  auto state5 = algo.Apply(State(state));
  ASSERT_EQ(state5.tops, state.tops);
  ASSERT_EQ(state5.grid, state.grid);
}
