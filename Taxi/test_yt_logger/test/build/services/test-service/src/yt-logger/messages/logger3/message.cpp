#include <yt-logger/messages/logger3/message.hpp>

#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/serialize/common_containers.hpp>

#include <yt-logger/timestamp.hpp>

namespace yt_logger {
namespace messages {

formats::json::Value logger3::SerializeToJson() const {
  formats::json::ValueBuilder json(formats::json::Type::kObject);

  json["timestamp"] = yt_logger::GetTimestampNowWithTz();
  json["value3"] = value3;
  json["value1"] = value1;
  json["value2"] = value2;
  json["value4"] = value4;
  json["value5"] = value5;

  return json.ExtractValue();
}

}
}
