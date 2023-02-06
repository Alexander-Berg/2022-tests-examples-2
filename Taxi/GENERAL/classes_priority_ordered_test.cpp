#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/classes_priority_ordered.hpp>
#include <config/config.hpp>
#include <models/classes.hpp>

TEST(TestClassesPriorityOrdered, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& classes_priority_ordered =
      config.Get<config::ClassesPriorityOrdered>();
  models::Classes classes;
  for (models::ClassType t = models::Classes::Unknown;
       t < models::Classes::MaxClassType; ++t)
    classes.Add(t);
  ASSERT_EQ(models::Classes::Unknown,
            classes_priority_ordered.GetMaxPriorityClass(classes));
}
