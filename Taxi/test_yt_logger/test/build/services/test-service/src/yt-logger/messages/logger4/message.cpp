#include <yt-logger/messages/logger4/message.hpp>

#include <userver/utils/encoding/tskv.hpp>

#include <yt-logger/timestamp.hpp>

namespace yt_logger {
namespace messages {

std::string logger4::SerializeToTskv() const {
  std::string result = "tskv\ttimestamp=" + yt_logger::GetTimestampNowWithTz();
  result.reserve(
      1024);  // log entry length approximation, better than default anyway

  result += "\tany_value=";
  utils::encoding::EncodeTskv(result, any_value,
                              utils::encoding::EncodeTskvMode::kValue);

  return result;
}

}
}
