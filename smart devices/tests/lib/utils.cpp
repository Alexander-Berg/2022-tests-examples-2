#include "utils.h"

#include <library/cpp/testing/common/env.h>
#include <util/random/entropy.h>
#include <util/random/mersenne.h>
#include <util/system/sysstat.h>

#include <sys/socket.h>
#include <sys/un.h>

namespace IOUpdater {
    std::string getSocketPath(const std::string& socketName) {
        TMersenne<ui64> rng(Seed());
        constexpr size_t maxUnixPathLen = sizeof(((sockaddr_un*)nullptr)->sun_path);
        std::string result = GetRamDrivePath();
        if (result.empty() || result.length() + socketName.length() > maxUnixPathLen) {
            result = GetWorkPath();
            if (result.length() + socketName.length() > maxUnixPathLen) {
                // See https://st.yandex-team.ru/DEVTOOLSSUPPORT-5680
                result = "/tmp/" + std::to_string(rng.GenRand64()) + "/";
                Mkdir(result.c_str(), MODE0777);
            }
        }
        return result + socketName;
    }

    std::string shortUtf8DebugString(const google::protobuf::Message& message) {
        google::protobuf::TextFormat::Printer printer;
        printer.SetUseUtf8StringEscaping(true);
        printer.SetSingleLineMode(true);
        printer.SetUseShortRepeatedPrimitives(true);
        printer.SetExpandAny(true);

        TString result = "{ ";
        google::protobuf::io::StringOutputStream output(&result);
        printer.Print(message, &output);
        result += '}';

        return result;
    }
    std::string getUniqueTestWorkdir() {
        TMersenne<ui64> rng(Seed());
        std::string result = GetWorkPath() + std::to_string(rng.GenRand64());
        Mkdir(result.c_str(), MODE0777);
        return result;
    }

} // namespace IOUpdater
