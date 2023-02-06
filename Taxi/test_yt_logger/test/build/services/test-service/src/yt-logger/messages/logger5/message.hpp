#pragma once

#include <cstdint>
#include <string>

#include <optional>

#include <fmt/format.h>

#include <userver/formats/json/value.hpp>
#include <yt-logger/message_types.hpp>

namespace yt_logger {
namespace messages {

struct logger5 final {
  /// No3
  std::string value3;

  static const MessageType message_type = MessageType::kJson;

  formats::json::Value SerializeToJson() const;

  static constexpr const char* kLoggerName = "yt-logger-logger5";

  std::string GetLoggerName() const { return std::string(kLoggerName); }
};

}
}
