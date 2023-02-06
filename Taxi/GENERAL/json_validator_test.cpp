#include "json_validator.hpp"

#include <exception>

#include <gtest/gtest.h>
#include <json/json.h>
#include <utils/helpers/json.hpp>

using helpers::ValidateJsonThrow;
using utils::helpers::ParseJson;

TEST(JsonValidator, BadObject) {
  const auto object = ParseJson(R"(
    {
      "dead10cc": {
        "deadbeef": "b16b00b5"
      }
    }
  )");
  auto schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "deadbeef": {
          "type": "object",
          "properties": {
            "dead10cc": {
              "type": "string"
            }
          }
        }
      }
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::out_of_range);

  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "b16b00b5": {
          "type": "string"
        },
        "deadbeef": {
          "type": "object",
          "properties": {
            "dead10cc": {
              "type": "string"
            }
          }
        }
      }
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::out_of_range);
}

TEST(JsonValidator, GoodObject) {
  auto object = Json::Value("dead10cc");
  auto schema = ParseJson(R"({"type": "string"})");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = ParseJson("{}");
  schema = ParseJson(R"({"type": "object", "properties": {}})");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = ParseJson(R"({"dead10cc": "deadbeef"})");
  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": "string"
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = ParseJson(R"({"dead10cc": {}})");
  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": "object",
          "properties": {}
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = ParseJson(R"(
    {
      "dead10cc": ["deadbeef", "baadcafe", "deadc0de"],
      "baadcafe": {
        "baadf00d": {
          "cafed00d": 3.1415,
          "deadc0de": {
            "deadfa11": ["deaddead", 3.1415, false, 69]
          },
          "deadbabe": false
        },
        "b16b00b5": 69
      }
    }
  )");
  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "baadcafe": {
          "type": "object",
          "properties": {
            "baadf00d": {
              "type": "object",
              "properties": {
                "cafed00d": {
                  "type": "number"
                },
                "deadc0de": {
                  "type": "object",
                  "properties": {
                    "deadfa11": {
                      "type": "array"
                    }
                  }
                },
                "deadbabe": {
                  "type": "boolean"
                }
              }
            },
            "b16b00b5": {
              "type": "integer"
            }
          }
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));
}

TEST(JsonValidator, UnlistedProperties) {
  const auto object = ParseJson(R"(
    {
      "deadbeef": "dead10cc",
      "baadcafe": "baadaa55"
    }
  )");
  const auto schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "deadbeef": {
          "type": "string"
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));
}

TEST(JsonValidator, SchemaTypes) {
  auto object = ParseJson(R"(
    {
      "dead10cc": 3.1415
    }
  )");
  auto schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": "number"
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = ParseJson(R"(
    {
      "dead10cc": 42
    }
  )");
  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": "integer"
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = ParseJson(R"(
    {
      "dead10cc": true
    }
  )");
  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": "boolean"
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = ParseJson(R"(
    {
      "dead10cc": ["first", "second"]
    }
  )");
  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = ParseJson(R"(
    {
      "dead10cc": null
    }
  )");
  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": "null"
        }
      }
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::domain_error);

  object = ParseJson(R"(
    {
      "dead10cc": null
    }
  )");
  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": ["null", "string"]
        }
      }
    }
  )");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));
}

TEST(JsonValidator, BadSchema) {
  auto object = ParseJson(R"(
    {
      "dead10cc": "deadbeef"
    }
  )");
  auto schema = ParseJson(R"(
    {
      "dead10cc": "string"
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::out_of_range);

  schema = ParseJson(R"(
    [{"dead10cc": "string"}]
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::invalid_argument);

  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": ["dead10cc"]
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::invalid_argument);

  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "type": 0
        }
      }
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::invalid_argument);

  schema = ParseJson(R"(
    {
      "type": "object",
      "props": {
        "dead10cc": {
          "type": "string"
        }
      }
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::out_of_range);

  schema = ParseJson(R"(
    {
      "type": "object",
      "properties": {
        "dead10cc": {
          "typo": "string"
        }
      }
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::out_of_range);
}
