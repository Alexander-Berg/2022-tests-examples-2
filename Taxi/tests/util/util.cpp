#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <taxi/tools/dorblu/lib/tests/helpers.h>

#include <taxi/tools/dorblu/lib/include/util.h>

#include <fstream>

#include <boost/filesystem.hpp>

TEST(Util, MonitoringEventTest)
{
    MonitoringEvent me {"blah01.example.com", "vhost500", MonitoringSeverity::Critical, "Lot's\nof\t\"errors\""};
    std::string excpectation = "{\"host\": \"blah01.example.com\", \"service\": \"vhost500\", \"status\": \"CRIT\", \"description\": \"Lot's\\nof\\t\\\"errors\\\"\"}";

    TestEquals("MonitoringEvent stringifiying", excpectation, me.asString());
}

void processTestCoroutine()
{
    std::string input = "123 456 789";
    while (input.size() < 65000) {
        input = input + input;
    }
    std::string output;
    int exitCode = std::numeric_limits<int>::min();

    async::Task(
        [&input, &output, &exitCode] {
            Process p({"/bin/cat"}, Process::StdIo::In | Process::StdIo::Out, "/tmp");

            p << input;
            output = p.getData();
            exitCode = p.join();
        }).join();

    TestEquals("Spawned process input and output", input, output);
    TestEquals("Spawned process exit code", static_cast<decltype(exitCode)>(0), exitCode);
}

TEST(Util, ProcessTest)
{
    async::Task task(processTestCoroutine);
    async::run();
}

TEST(Util, JugglerSenderTest)
{
    JugglerSender js;

    js << MonitoringEvent{"blah01.example.com", "vhost500", MonitoringSeverity::Critical, "Many errors"};
    js << MonitoringEvent{"blah02.example.com", "vhost499", MonitoringSeverity::Critical, "Extremely many errors"};
    js << MonitoringEvent{"blah03.example.com", "vhost500", MonitoringSeverity::Critical, "Not so many errors"};

    const auto& events = js.events();
    TestEquals("JugglerSender events amount", static_cast<size_t>(3), events.size());

    std::stringstream expected;
    expected << "JugglerSender<[" << events[0] << ", " << events[1] <<  ", " << events[2] << "]>";
    TestEquals("JugglerSender json serialization", expected.str(), static_cast<std::string>(js));
}
