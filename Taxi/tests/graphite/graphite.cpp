#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <taxi/tools/dorblu/lib/include/graphite.h>

#include <string>
#include <iostream>

bool compareStrings(const std::string& desired, const std::string& got)
{
    if (desired != got) {
        std::cout << "failed." << std::endl;
        std::cout << "Expected string:\n" << desired <<
                     "But got string:\n" << got << std::endl;
        return false;
    } else {
        std::cout << "ok." << std::endl;
        return true;
    }
}

TEST(Graphite, GraphiteTestCase)
{
    GraphiteMetrics gm;

    /* Test 1: initialization */
    gm.setProject("maps");
    gm.setGroup("maps_mobile");
    gm.setHostname("spdy3.mob.maps.yandex.net");
    gm.setRegion("");

    gm.push("timings.ups", 1234.0);
    gm.push("timings.req", 2345.0);
    gm.push("ok_rps.rps", 3456);

    const std::string desiredResult1 =
        "cluster.geo.maps.maps_mobile.spdy3_mob_maps_yandex_net.timings.ups 1234.000000 987\n"
        "cluster.geo.maps.maps_mobile.spdy3_mob_maps_yandex_net.timings.req 2345.000000 987\n"
        "cluster.geo.maps.maps_mobile.spdy3_mob_maps_yandex_net.ok_rps.rps 3456 987\n"
    ;

    EXPECT_TRUE(compareStrings(desiredResult1, gm.prepareMetrics(987)));

    /* Test 2: changing region and append more metrics */
    gm.setRegion("iva");

    gm.push("timings.ups", 1234.0);
    gm.push("timings.req", 2345.0);
    gm.push("ok_rps.rps", 3456);

    const std::string desiredResult2 =
        desiredResult1 +
        "cluster.geo.maps.maps_mobile.spdy3_mob_maps_yandex_net-iva.timings.ups 1234.000000 987\n" +
        "cluster.geo.maps.maps_mobile.spdy3_mob_maps_yandex_net-iva.timings.req 2345.000000 987\n" +
        "cluster.geo.maps.maps_mobile.spdy3_mob_maps_yandex_net-iva.ok_rps.rps 3456 987\n"
    ;

    EXPECT_TRUE(compareStrings(desiredResult2, gm.prepareMetrics(987)));
}
