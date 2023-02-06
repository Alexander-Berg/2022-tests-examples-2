#include <yt-logger/messages/logger1/message.hpp>

#include <userver/utils/encoding/tskv.hpp>

#include <yt-logger/timestamp.hpp>

namespace yt_logger {
namespace messages {

std::string logger1::SerializeToTskv() const {
  std::string result = "tskv\ttimestamp=" + yt_logger::GetTimestampNowWithTz();
  result.reserve(
      1024);  // log entry length approximation, better than default anyway

  if (bool_value) {
    result += "\tbool_value=";
    utils::encoding::EncodeTskv(result,
                                std::string((*bool_value) ? "true" : "false"),
                                utils::encoding::EncodeTskvMode::kValue);
  }
  return result;
}

}
}
