#pragma once

#include <cstdint>
#include <string>

#include <optional>

#include <fmt/format.h>

#include <yt-logger/message_types.hpp>

namespace yt_logger {
namespace messages {

struct logger_sev_tops_3 final {
  /// No
  std::string bool_value;

  static const MessageType message_type = MessageType::kTskv;

  std::string SerializeToTskv() const;

  static constexpr const char* kLoggerName = "yt-logger-logger_sev_tops_3";

  std::string GetLoggerName() const { return std::string(kLoggerName); }
};

}
}
