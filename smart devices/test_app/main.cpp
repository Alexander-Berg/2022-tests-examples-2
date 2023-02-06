#include <smart_devices/tools/updater/logging/utils.h>
#include <smart_devices/tools/updater/lib/updater.h>
#include <smart_devices/tools/updater/lib/utils.h>
#include <curl/curl.h>
#include <iostream>

using namespace IOUpdater;

int main(int argc, char** argv) {
    signal(SIGPIPE, SIG_IGN); // N.B.: Need to ignore SIGPIPE due to libcurl/libssl behaviour
    // FIXME: Think about moving this somewhere in lib
    initLogging(spdlog::level::trace);
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <workdir> <update_url>";
        return 1;
    }

    curl_global_init(CURL_GLOBAL_DEFAULT);
    UpdaterConfig config{};
    config.workDir = argv[1];
    config.downloadDir = config.workDir;
    config.ipcSocketPath = config.workDir + "/updater.sock";
    config.updateUrl = argv[2];
    config.deviceId = "FF98F029EB01F30374FFF9F1";
    config.platform = "yandexmini";
    config.updateApplicationTimeout = std::chrono::milliseconds(20);
    config.updateApplicationHardTimeout = std::chrono::milliseconds(20);

    Updater updater(config);
    updater.start();
    waitForSignals({SIGTERM, SIGINT});
    curl_global_cleanup();
}