#pragma once

#include <cstdint>
#include <string>

#include <optional>

#include <fmt/format.h>

#include <yt-logger/message_types.hpp>

namespace yt_logger {
namespace messages {

struct logger_sev_tops_1 final {
  /// No
  std::string bool_value;

  static const MessageType message_type = MessageType::kTskv;

  std::string SerializeToTskv() const;

  std::string GetLoggerName() const {
    if (logger_section_.empty()) {
      return logger_prefix_;
    } else {
      return fmt::format("{}__{}", logger_prefix_, logger_section_);
    }
  }

  void SetLoggerName(std::string logger_name) {
    logger_section_ = std::move(logger_name);
  }

 private:
  std::string logger_prefix_ = "yt-logger-logger_sev_tops_1";
  std::string logger_section_ = "name1";
};

}
}
