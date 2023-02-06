#include <yt-logger/messages/logger5/message.hpp>

#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/serialize/common_containers.hpp>

#include <yt-logger/timestamp.hpp>

namespace yt_logger {
namespace messages {

formats::json::Value logger5::SerializeToJson() const {
  formats::json::ValueBuilder json(formats::json::Type::kObject);

  json["timestamp"] = yt_logger::GetTimestampNowWithTz();
  json["value3"] = value3;

  return json.ExtractValue();
}

}
}
