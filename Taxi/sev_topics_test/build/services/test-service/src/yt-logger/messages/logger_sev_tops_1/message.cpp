#include <yt-logger/messages/logger_sev_tops_1/message.hpp>

#include <userver/utils/encoding/tskv.hpp>

#include <yt-logger/timestamp.hpp>

namespace yt_logger {
namespace messages {

std::string logger_sev_tops_1::SerializeToTskv() const {
  std::string result =
      "tskv\ttimestamp=" + yt_logger::GetTimestampNowPrecision6WithTz();
  result.reserve(
      1024);  // log entry length approximation, better than default anyway

  result += "\tbool_value=";
  utils::encoding::EncodeTskv(result, bool_value,
                              utils::encoding::EncodeTskvMode::kValue);

  return result;
}

}
}
