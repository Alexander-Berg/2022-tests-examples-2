#include <gtest/gtest.h>

#include <algorithm>
#include <cctype>
#include <string>

#include <userver/formats/json/string_builder.hpp>
#include <userver/logging/log.hpp>
#include <web_constructor/web_constructor.hpp>

const std::string kSampleWebConstructor = R"(
{
    "root_block": {
        "payload": {
            "orientation": "vertical",
            "children_blocks": [
                {
                    "web_constructor_block_kind": "text_line",
                    "payload": {
                        "text": "BoldTextLine",
                        "is_bold": true
                    }
                },
                {
                    "web_constructor_block_kind": "key_value",
                    "payload": {
                        "key_title": "Key",
                        "value_block": {
                            "web_constructor_block_kind": "text_line",
                            "payload": {
                                "text": "Value"
                            }
                        }
                    }
                },
                {
                    "web_constructor_block_kind": "spacer"
                },
                {
                    "web_constructor_block_kind": "line",
                    "payload": {
                        "orientation": "horizontal"
                    }
                },
                {
                    "web_constructor_block_kind": "list",
                    "payload": {
                        "orientation": "horizontal",
                        "children_blocks": [
                            {
                                "web_constructor_block_kind": "text_line",
                                "payload": {
                                    "text": "1"
                                }
                            },
                            {
                                "web_constructor_block_kind": "text_line",
                                "payload": {
                                    "text": "2"
                                }
                            },
                            {
                                "web_constructor_block_kind": "text_line",
                                "payload": {
                                    "text": "3"
                                }
                            }
                        ]
                    }
                }
            ]
        },
        "web_constructor_block_kind": "list"
    }
}
)";

namespace tests {
TEST(Sample, Simpe) {
  auto builder = web_constructor::WebConstructorBuilder::MakeWithRoot<
      web_constructor::WebConstructorBlockList>(
      /*orientation=*/web_constructor::Orientation::kVertical);

  builder.Root().AddChild<web_constructor::WebConstructorBlockTextLine>(
      /*text=*/"BoldTextLine",
      /*is_bold=*/true);

  builder.Root()
      .AddChild<web_constructor::WebConstructorBlockKeyValue>(
          /*key_title=*/"Key")
      .SetValue<web_constructor::WebConstructorBlockTextLine>(
          /*text=*/"Value");

  builder.Root().AddChild<web_constructor::WebConstructorBlockSpacer>();
  builder.Root().AddChild<web_constructor::WebConstructorBlockLine>();

  auto& horizontal_list =
      builder.Root().AddChild<web_constructor::WebConstructorBlockList>(
          /*orientation=*/web_constructor::Orientation::kHorizontal);
  horizontal_list.AddChild<web_constructor::WebConstructorBlockTextLine>(
      /*text=*/"1");
  horizontal_list.AddChild<web_constructor::WebConstructorBlockTextLine>(
      /*text=*/"2");
  horizontal_list.AddChild<web_constructor::WebConstructorBlockTextLine>(
      /*text=*/"3");

  formats::json::StringBuilder sb;
  WriteToStream(builder.ExtractValue(), sb);

  // Remove whitespaces
  std::string expected_string = kSampleWebConstructor;
  expected_string.erase(
      std::remove_if(
          expected_string.begin(), expected_string.end(),
          [](char c) { return std::isspace(static_cast<unsigned char>(c)); }),
      expected_string.end());

  ASSERT_EQ(sb.GetString(), expected_string);
}
}  // namespace tests
