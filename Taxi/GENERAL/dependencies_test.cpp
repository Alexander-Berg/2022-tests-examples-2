#include "dependencies.hpp"

#include <userver/utest/utest.hpp>

#include <stdexcept>

namespace agl::sourcing::tests {

TEST(TestDependencies, CircularDependenciesDetector) {
  auto source_id_to_human_readable = [](const size_t i) -> const std::string& {
    static const std::vector<std::string> kNames{"src-0", "src-1", "src-2",
                                                 "src-3"};
    return kNames[i];
  };

  // trivial case
  {
    Dependencies dependencies;
    EXPECT_NO_THROW(
        dependencies.CheckCircularDependencies(source_id_to_human_readable));
  }

  // other cases
  using Case = std::pair<std::vector<std::pair<size_t, size_t>>, bool>;
  static const std::vector<Case> kCases{
      // with loops
      {{{0, 1}, {1, 0}}, true},
      {{{0, 1}, {1, 2}, {2, 3}, {3, 0}}, true},
      {{{0, 1}, {1, 0}}, true},

      // no loops
      {{{0, 1}, {0, 1}}, false},
      {{{0, 1}, {1, 2}, {2, 3}}, false},
      {{{0, 1}}, false},
  };

  // run test cases
  for (const Case& c : kCases) {
    Dependencies dependencies;
    for (const std::pair<size_t, size_t>& dep : c.first) {
      dependencies.SetDependency(dep.first, dep.second,
                                 source_id_to_human_readable);
    }

    if (c.second) {
      EXPECT_THROW(
          dependencies.CheckCircularDependencies(source_id_to_human_readable),
          std::runtime_error);
    } else {
      EXPECT_NO_THROW(
          dependencies.CheckCircularDependencies(source_id_to_human_readable));
    }
  }
}

}  // namespace agl::sourcing::tests
