#pragma once

#include <cstdint>
#include <string>

#include <optional>

#include <fmt/format.h>

#include <yt-logger/message_types.hpp>

namespace yt_logger {
namespace messages {

struct logger1 final {
  /// No
  std::optional<bool> bool_value;

  static const MessageType message_type = MessageType::kTskv;

  std::string SerializeToTskv() const;

  static constexpr const char* kLoggerName = "yt-logger-logger1";

  std::string GetLoggerName() const { return std::string(kLoggerName); }
};

}
}
