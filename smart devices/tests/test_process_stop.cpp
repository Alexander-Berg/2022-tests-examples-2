#include <smart_devices/tools/launcher2/lib/process.h>

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>
#include <util/system/fs.h>

#include <thread>

Y_UNIT_TEST_SUITE(TestProcess) {
    Y_UNIT_TEST(Stop) {
        const std::string markerFile = GetWorkPath() + "/started";
        Process p("stubborn_app", BinaryPath("smart_devices/tools/launcher2/lib/tests/stubborn_app/stubborn_app"),
                  {markerFile}, GetWorkPath(), false, "", 0, std::nullopt);
        p.start();
        while (!NFs::Exists(TString{markerFile})) {
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        }

        p.stop(std::chrono::seconds(5));
    }
}
