#pragma once

#include <cstdint>
#include <string>

#include <optional>

#include <fmt/format.h>

#include <userver/formats/json/value.hpp>
#include <yt-logger/message_types.hpp>

#include <core/object.hpp>

namespace yt_logger {
namespace messages {

struct logger3 final {
  /// No3
  std::string value3;
  /// No1
  std::uint64_t value1;
  /// No2
  double value2;
  /// No4
  std::int64_t value4;
  /// No5
  std::vector<core::Object> value5;

  static const MessageType message_type = MessageType::kJson;

  formats::json::Value SerializeToJson() const;

  static constexpr const char* kLoggerName = "yt-logger-logger3";

  std::string GetLoggerName() const { return std::string(kLoggerName); }
};

}
}
