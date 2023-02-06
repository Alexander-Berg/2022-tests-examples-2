#include <smart_devices/tools/launcher2/lib/launcher.h>

#include <fstream>
#include <iostream>

int main(int argc, char** argv) {
    initLogging();
    if (argc < 3) {
        std::cerr << "Usage: quasar_launcher2 <config file> <max restarting duration>";
        return 1;
    }
    std::string filename = argv[1];
    std::chrono::seconds maxDuration(atoll(argv[2]));
    std::string node = "main";
    std::string script;
    std::string bin;

    std::ifstream file(filename);
    if (!file) {
        std::cerr << "failed to open file " << filename << std::endl;
        return 1;
    }

    Json::CharReaderBuilder builder;
    Json::Value root;
    builder["collectComments"] = false;
    JSONCPP_STRING errs;

    if (!parseFromStream(builder, file, &root, &errs)) {
        std::cerr << "cannot read file '" << filename << "'" << std::endl;
        std::cerr << errs << std::endl;
        return 1;
    }

    Launcher launcher(tasksParamsFromJson(root["nodes"][0]["tasks"]));
    launcher.workLoop(maxDuration);
    return 0;
}
