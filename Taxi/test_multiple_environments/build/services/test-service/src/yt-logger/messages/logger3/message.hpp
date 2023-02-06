#pragma once

#include <cstdint>
#include <string>

#include <optional>

#include <fmt/format.h>

#include <yt-logger/message_types.hpp>

namespace yt_logger {
namespace messages {

struct logger3 final {
  /// No3
  std::string value3;
  /// No1
  std::uint64_t value1;
  /// No2
  double value2;

  static const MessageType message_type = MessageType::kTskv;

  std::string SerializeToTskv() const;

  static constexpr const char* kLoggerName = "yt-logger-logger3";

  std::string GetLoggerName() const { return std::string(kLoggerName); }
};

}
}
