#include <gtest/gtest.h>

#include "radio/blocks/commutation/out_points.hpp"
#include "radio/blocks/utils/buffers.hpp"
#include "radio/blocks/utils/description_prioritizer.hpp"

namespace hejmdal::radio::blocks {

TEST(TestDescriptionPrioritizer, TestDescriptionPrioritizer) {
  formats::json::ValueBuilder builder;
  builder["type"] = "description_prioritizer";
  builder["id"] = "description_prioritizer";

  builder["array_key"] = "array";
  builder["priority_key"] = "priority";
  builder["description_key"] = "description";

  auto test = std::make_shared<DescriptionPrioritizer>(builder.ExtractValue());
  auto exit = std::make_shared<StateBuffer>("");
  test->OnStateOut(exit);

  {
    // normal situation
    formats::json::ValueBuilder meta{formats::common::Type::kObject};
    meta["array"].Resize(3);
    meta["array"][0]["priority"] = 0.3;
    meta["array"][0]["description"] = "wrong";
    meta["array"][1]["priority"] = 0.5;
    meta["array"][1]["description"] = "correct";
    meta["array"][2]["priority"] = 0.2;
    meta["array"][2]["description"] = "wrong";

    test->StateIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(),
                  State(State::Value::kOk, "old"));
    ASSERT_EQ(exit->LastState().GetDescription(), "correct");
  }

  {
    // no array_key
    formats::json::ValueBuilder meta{formats::common::Type::kObject};

    test->StateIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(),
                  State(State::Value::kOk, "old"));
    ASSERT_EQ(exit->LastState().GetDescription(), "old");
  }

  {
    // not an array in array_key
    formats::json::ValueBuilder meta{formats::common::Type::kObject};
    meta["array"] = "not an array";

    test->StateIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(),
                  State(State::Value::kOk, "old"));
    ASSERT_EQ(exit->LastState().GetDescription(), "old");
  }

  {
    // no strings in array
    formats::json::ValueBuilder meta{formats::common::Type::kObject};
    meta["array"].Resize(3);
    meta["array"][0] = 0.5;
    meta["array"][1] = formats::common::Type::kArray;
    meta["array"][2] = formats::common::Type::kObject;

    test->StateIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(),
                  State(State::Value::kWarn, "old"));
    ASSERT_EQ(exit->LastState().GetDescription(), "old");
  }
}

}  // namespace hejmdal::radio::blocks
