package ru.yandex.autotests.tuneapitests.region;


import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.tuneapitests.steps.ClientSteps;
import ru.yandex.autotests.tuneapitests.steps.RegionSteps;
import ru.yandex.autotests.tuneapitests.utils.Authorized;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneapitests.utils.Region;
import ru.yandex.autotests.tuneclient.TuneClient;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.unauth;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Change History Region")
@RunWith(Parameterized.class)
@Features("Region")
@Stories("Change History Region")
public class ChangeHistoryRegionTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Region: \"{1}\"->\"{2}\"->\"{3}\"->\"{4}\"->\"{5}\"; {6}; Retpath: {7}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Authorized auth : Authorized.values()) {
                data.add(new Object[]{d, Region.SPB, Region.BREST,Region.ALMATA, Region.PSKOV, Region.GOMEL, auth, null});
                data.add(new Object[]{d, Region.BREST, Region.KARAGANDA,Region.LVOV, Region.ODESSA, Region.PSKOV, auth, d.getYandexUrl()});
            }
        }
        return data;
    }

    private final Client client;
    private final Domain domain;
    private final Region region1;
    private final Region region2;
    private final Region region3;
    private final Region region4;
    private final Region region5;
    private final Authorized authorized;
    private final String retpath;
    private final ClientSteps userClient;
    private final RegionSteps userRegion;

    public ChangeHistoryRegionTest(Domain domain, Region region1, Region region2, Region region3, Region region4, Region region5,
                                   Authorized authorized, String retpath)
    {
        this.domain = domain;
        this.region1 = region1;
        this.region2 = region2;
        this.region3 = region3;
        this.region4 = region4;
        this.region5 = region5;
        this.authorized = authorized;
        this.retpath = retpath;
        this.client = TuneClient.getClient();
        this.userClient = new ClientSteps(client);
        this.userRegion = new RegionSteps(client, domain);
    }

    @Before
    public void setUp() {
        userClient.get(domain.getYandexUrl());
        userClient.authIfNeeded(authorized, domain);
        userRegion.setRegion(region1, retpath);
        userRegion.shouldSeeRegionId(region1.getRegionId());
        userRegion.setRegion(region2, retpath);
        userRegion.shouldSeeRegionId(region2.getRegionId());
        userRegion.setRegion(region3, retpath);
        userRegion.shouldSeeRegionId(region3.getRegionId());
        userRegion.setRegion(region4, retpath);
        userRegion.shouldSeeRegionId(region4.getRegionId());
        userRegion.setRegion(region5, retpath);
        userRegion.shouldSeeRegionId(region5.getRegionId());
    }

    @Test
    public void lastFourChangedRegions() {
        userRegion.shouldSeeRegionIdWithMy(region5.getRegionId(),
                Arrays.asList(region5.getRegionId(), region4.getRegionId(), region3.getRegionId(), region2.getRegionId()));
    }

}
