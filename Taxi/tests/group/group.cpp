#include <taxi/tools/dorblu/lib/tests/testbase.h>
#include <taxi/tools/dorblu/lib/tests/helpers.h>

#include <taxi/tools/dorblu/lib/include/group.h>

#include <maps/libs/log8/include/log8.h>
#include <chrono>
#include <iostream>

std::string emulateGraphite(const TSocketHolder& listenFd)
{
    std::string dataBuf(1 << 13, '\0');
    async::read(listenFd, &(dataBuf.front()), dataBuf.capacity(), TDuration::Seconds(30));

    DEBUG() << "Read " << dataBuf.size() << " bytes of " << dataBuf.capacity() << ".";

    return dataBuf;
}

TEST(Group, GroupTest)
{
    auto listenPortHolder = NTesting::GetFreePort();
    auto graphitePortHolder = NTesting::GetFreePort();
    int listenPort = static_cast<int>(listenPortHolder);
    int graphitePort = static_cast<int>(graphitePortHolder);

    auto bsonFilter = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto bsonTimingsLimits = bson::object("Percentile", 0.99, "Warn", 0.01, "Crit", 0.300, "Type", "Req");
    auto bsonTimingsLimits2 = bson::object("Percentile", 0.99, "Warn", 0.01, "Crit", 0.300, "Type", "Ssl");
    auto bsonOptions = bson::object("Timings", bson::array(bsonTimingsLimits, bsonTimingsLimits2));
    auto bsonRule = bson::object("name", "myRule", "filter", bsonFilter, "Options", bsonOptions);
    auto rulesArray = bson::array(bsonRule);
    auto bsonHost1 = bson::object("fqdn", "localhost", "dc", "dc1");
    auto bsonHost2 = bson::object("fqdn", "localhost", "dc", "dc2");
    auto hostsArray = bson::array(bsonHost1, bsonHost2);
    auto bsonGroup = bson::object("group", "myGroup", "project", "myProject", "rules", rulesArray, "hosts", hostsArray);

    async::Task task(
        [listenPort, graphitePort, &bsonGroup] {
            async::Listener listener(TNetworkAddress(listenPort), listenForHost);
            async::Listener graphiteListener(TNetworkAddress(graphitePort),
                [] (const TSocketHolder& s) { std::cout << emulateGraphite(s) << std::endl; });

            SolomonSpack solomon;
            Group group(bsonGroup, solomon, listenPort);
            group.run();
            group.wait();
        });
    async::run();
}
