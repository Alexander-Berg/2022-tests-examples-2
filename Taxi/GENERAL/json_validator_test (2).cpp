#include "json_validator.hpp"

#include <exception>

#include <gtest/gtest.h>

#include <userver/formats/json.hpp>

using formats::json::FromString;
using models::ValidateJsonThrow;

TEST(JsonValidator, BadObject) {
  const auto object = FromString(R"(
    {
      "dead10cc": {
        "deadbeef": "b16b00b5"
      }
    }
  )");
  auto schema = FromString(R"(
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

  schema = FromString(R"(
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
  auto object = FromString("{}");
  auto schema = FromString(R"({"type": "object", "properties": {}})");

  EXPECT_NO_THROW(ValidateJsonThrow(object, schema));

  object = FromString(R"({"dead10cc": "deadbeef"})");
  schema = FromString(R"(
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

  object = FromString(R"({"dead10cc": {}})");
  schema = FromString(R"(
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

  object = FromString(R"(
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
  schema = FromString(R"(
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
  const auto object = FromString(R"(
    {
      "deadbeef": "dead10cc",
      "baadcafe": "baadaa55"
    }
  )");
  const auto schema = FromString(R"(
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
  auto object = FromString(R"(
    {
      "dead10cc": 3.1415
    }
  )");
  auto schema = FromString(R"(
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

  object = FromString(R"(
    {
      "dead10cc": 42
    }
  )");
  schema = FromString(R"(
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

  object = FromString(R"(
    {
      "dead10cc": true
    }
  )");
  schema = FromString(R"(
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

  object = FromString(R"(
    {
      "dead10cc": ["first", "second"]
    }
  )");
  schema = FromString(R"(
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

  object = FromString(R"(
    {
      "dead10cc": null
    }
  )");
  schema = FromString(R"(
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

  object = FromString(R"(
    {
      "dead10cc": null
    }
  )");
  schema = FromString(R"(
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
  auto object = FromString(R"(
    {
      "dead10cc": "deadbeef"
    }
  )");
  auto schema = FromString(R"(
    {
      "dead10cc": "string"
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::out_of_range);

  schema = FromString(R"(
    [{"dead10cc": "string"}]
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::invalid_argument);

  schema = FromString(R"(
    {
      "type": "object",
      "properties": ["dead10cc"]
    }
  )");

  EXPECT_THROW(ValidateJsonThrow(object, schema), std::invalid_argument);

  schema = FromString(R"(
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

  schema = FromString(R"(
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

  schema = FromString(R"(
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
