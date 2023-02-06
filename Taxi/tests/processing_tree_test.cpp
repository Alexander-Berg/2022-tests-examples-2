#include <gtest/gtest.h>

#include "processing_tree.hpp"

namespace sensitive_data_masking {

namespace {

size_t AddPathToTree(ProcessingTree& tree, const JsonPath& path) {
  size_t nodes_added = 0;
  for (const auto& level : path) {
    auto success = tree.AddLevelToCurrentPath(level);
    if (success) {
      ++nodes_added;
    } else {
      break;
    }
  }
  return nodes_added;
}

void RemovePathFromTree(ProcessingTree& tree, size_t num_nodes) {
  for (size_t i = 0; i < num_nodes; ++i) {
    tree.RemoveLastLevelFromCurrentPath();
  }
}

void CheckTreeHasPath(ProcessingTree& tree, const JsonPath& path,
                      bool expected) {
  const auto nodes_added = AddPathToTree(tree, path);

  EXPECT_EQ(nodes_added == path.size(), expected);

  RemovePathFromTree(tree, nodes_added);
}

void CheckTreeShouldMaskPath(ProcessingTree& tree, const JsonPath& path,
                             bool expected) {
  const auto nodes_added = AddPathToTree(tree, path);

  EXPECT_EQ(tree.ShouldProcessCurrentPath(), expected);

  RemovePathFromTree(tree, nodes_added);
}

}  // namespace

TEST(TestMaskingTree, CheckEmptyTree) {
  auto tree = ProcessingTree({});

  CheckTreeHasPath(tree, {""}, false);
  CheckTreeHasPath(tree, {"phone"}, false);
  CheckTreeHasPath(tree, {"user", "phone"}, false);

  // empty path exists in any tree
  CheckTreeHasPath(tree, {}, true);
}

TEST(TestMaskingTree, CheckSimpleTree) {
  const std::vector<JsonPath>& paths = {{"phone"}};
  auto tree = ProcessingTree(paths);

  CheckTreeHasPath(tree, {}, true);
  CheckTreeHasPath(tree, {"phone"}, true);

  CheckTreeHasPath(tree, {"phone", "number"}, false);
}

TEST(TestMaskingTree, CheckShouldMask) {
  const std::vector<JsonPath>& paths = {
      {"brandings", "profile", "badge_title"},
      {"brandings", "profile", "badge_subtitle"},
      {"brandings", "profile", "badge_image_tag"},
      {"brandings", "profile", "title_badge_tag"},
  };

  auto tree = ProcessingTree(paths);

  CheckTreeHasPath(tree, {"brandings"}, true);
  CheckTreeHasPath(tree, {"brandings", "profile"}, true);
  CheckTreeHasPath(tree, {"brandings", "profile", "badge_title"}, true);

  CheckTreeShouldMaskPath(tree, {"brandings"}, false);
  CheckTreeShouldMaskPath(tree, {"brandings", "profile"}, false);
  CheckTreeShouldMaskPath(tree, {"brandings", "profile", "missing"}, false);
  CheckTreeShouldMaskPath(tree, {"brandings", "profile", "badge_title"}, true);

  CheckTreeHasPath(tree, {"subscriptions"}, false);
  CheckTreeShouldMaskPath(tree, {"subscriptions"}, false);
}

TEST(TestMaskingTree, CheckShouldMaskNestedPath) {
  const std::vector<JsonPath>& paths_growing = {
      {"brandings"},
      {"brandings", "profile"},
  };
  const std::vector<JsonPath>& paths_shrinking = {
      {"brandings", "profile"},
      {"brandings"},
  };

  for (const auto& paths : {paths_growing, paths_shrinking}) {
    auto tree = ProcessingTree(paths);

    CheckTreeHasPath(tree, {"brandings"}, true);
    CheckTreeHasPath(tree, {"brandings", "profile"}, false);
  }
}

}  // namespace sensitive_data_masking
