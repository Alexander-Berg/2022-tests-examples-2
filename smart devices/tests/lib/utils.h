#pragma once

#include <google/protobuf/message.h>
#include <google/protobuf/text_format.h>

#include <string>

namespace IOUpdater {
    std::string getSocketPath(const std::string& socketName);
    std::string getUniqueTestWorkdir();
    std::string shortUtf8DebugString(const google::protobuf::Message& message);
} // namespace IOUpdater
