#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <taxi/tools/dorblu/lib/tests/helpers.h>

#include <taxi/tools/dorblu/lib/include/util.h>

#include <fstream>

#include <boost/filesystem.hpp>

void testJugglerQueue()
{
    std::string output;
    int exitCode = std::numeric_limits<int>::min();

    std::ifstream apdexAlertsDataFile("files/sample_apdex_alerting_data.json");
    std::string apdexAlertsData;
    std::string errors;

    std::string tmp;
    while (std::getline(apdexAlertsDataFile, tmp))
        apdexAlertsData += tmp + '\n';

    async::Task(
        [&apdexAlertsData, &output, &errors, &exitCode] {
            Process p({"/usr/bin/juggler_queue_event", "--batch"}, Process::StdIo::In | Process::StdIo::Out | Process::StdIo::Err, "/tmp");

            p << apdexAlertsData;
            errors = p.getErr();
            output = p.getData();
            exitCode = p.join();
        }).join();

    std::string errorStr = "error";
    EXPECT_TRUE(std::search(errors.begin(), errors.end(), errorStr.begin(), errorStr.end(),
        [](char c1, char c2) { return std::tolower(c1) == std::tolower(c2); }) == errors.end());
    TestEquals("Stdout from juggler_queue_event", {""}, output);
}

TEST(Juggler, JugglerQueueTest)
{
    if (!boost::filesystem::exists("/usr/bin/juggler_queue_event")) {
      GTEST_SKIP();
    }

    async::Task task(testJugglerQueue);
    async::run();
}
