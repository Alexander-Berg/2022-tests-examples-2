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
@Aqua.Test(title = "Change Region")
@RunWith(Parameterized.class)
@Features("Region")
@Stories("Change Region")
public class ChangeRegionTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Region: \"{1}\" -> \"{2}\"; {3}; Retpath: {4}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Region r1 : Region.values()) {
                for (Region r2 : Region.values()) {
                    if (!r1.equals(r2)) {
                        for (Authorized auth : Authorized.values()) {
                            data.add(new Object[]{d, r1, r2, auth, null});
                            data.add(new Object[]{d, r1, r2, auth, d.getYandexUrl()});
                        }
                    }
                }
            }
        }
        return data;
    }

    private final Client client;
    private final Domain domain;
    private final Region region1;
    private final Region region2;
    private final Authorized authorized;
    private final String retpath;
    private final ClientSteps userClient;
    private final RegionSteps userRegion;

    public ChangeRegionTest(Domain domain, Region region1, Region region2, Authorized authorized, String retpath) {
        this.domain = domain;
        this.region1 = region1;
        this.region2 = region2;
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
    }

    @Test
    @Stories("Change Region")
    public void changeRegion() {
        userRegion.setRegion(region2, retpath);
        userRegion.shouldSeeRegionIdWithMy(region2.getRegionId(), Arrays.asList(region2.getRegionId(), region1.getRegionId()));
    }

    @Test
    @Stories("Change Region With Unauth sk in auth mode")
    public void regionChangedWithUnauthSk() {
        assumeThat(authorized, equalTo(Authorized.AUTH));
        userRegion.setRegionWithWrongSk(region2, unauth(domain, client), retpath);
        userRegion.shouldSeeRegionIdWithMy(region2.getRegionId(), Arrays.asList(region2.getRegionId(), region1.getRegionId()));
    }

}
