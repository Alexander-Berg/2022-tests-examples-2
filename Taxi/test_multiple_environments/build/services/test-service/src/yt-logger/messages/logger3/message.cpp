#include <yt-logger/messages/logger3/message.hpp>

#include <userver/utils/encoding/tskv.hpp>

#include <yt-logger/timestamp.hpp>

namespace yt_logger {
namespace messages {

std::string logger3::SerializeToTskv() const {
  std::string result = "tskv\ttimestamp=" + yt_logger::GetTimestampNowWithTz();
  result.reserve(
      1024);  // log entry length approximation, better than default anyway

  result += "\tvalue3=";
  utils::encoding::EncodeTskv(result, value3,
                              utils::encoding::EncodeTskvMode::kValue);

  result += "\tvalue1=";
  utils::encoding::EncodeTskv(result, std::to_string(value1),
                              utils::encoding::EncodeTskvMode::kValue);

  result += "\tvalue2=";
  utils::encoding::EncodeTskv(result, std::to_string(value2),
                              utils::encoding::EncodeTskvMode::kValue);

  return result;
}

}
}
