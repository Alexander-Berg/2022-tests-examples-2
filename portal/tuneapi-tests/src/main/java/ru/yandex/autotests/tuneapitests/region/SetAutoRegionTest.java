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
import java.util.Collection;
import java.util.EnumSet;
import java.util.List;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.nullValue;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Set Auto Region")
@RunWith(Parameterized.class)
@Features("Region")
@Stories("Set Auto Region")
public class SetAutoRegionTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Region: \"{1}\"; {2}; Retpath: {3}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Region r : Region.values()) {
                for (Authorized auth : Authorized.values()) {
                    data.add(new Object[]{d, r, auth, null});
                    data.add(new Object[]{d, r, auth, d.getYandexUrl()});
                }
            }
        }
        return data;
    }

    private final Client client;
    private final Domain domain;
    private final Region region;
    private final Authorized authorized;
    private final String retpath;
    private final ClientSteps userClient;
    private final RegionSteps userRegion;

    private String actualRegionId;

    public SetAutoRegionTest(Domain domain, Region region, Authorized authorized, String retpath) {
        this.domain = domain;
        this.region = region;
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
        actualRegionId = userRegion.getActualRegionId();
    }

    @Test
    public void setAuto() {
        userRegion.setRegion(region, retpath);
        userRegion.shouldSeeRegionId(region.getRegionId());

        userRegion.setAuto("1", retpath);
        userRegion.shouldSeeRegionId(anyOf(equalTo(actualRegionId), nullValue()));
    }
}
