#include <library/cpp/testing/unittest/tests_data.h>

#include <taxi/tools/dorblu/lib/tests/testbase.h>
#include <taxi/tools/dorblu/lib/tests/helpers.h>

#include <string>

TEST(Host, HostTest)
{
    auto portHolder = NTesting::GetFreePort();
    int port = static_cast<int>(portHolder);
    auto host = getHost(port);

    const auto& stats = host.message().rules().front().stats();
    const auto& okRps = stats.requests().at("maps_ok_rps.rps");
    const auto& requestTimings = stats.timings().at("maps_ok_request_timings");

    TestEquals("maps_ok_rps.rps in Host", static_cast<uint64_t>(5), okRps.count());
    TestEquals("maps_ok_request_timings in Host", static_cast<size_t>(5), requestTimings.timings().size());
}
