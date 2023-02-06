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
import java.util.List;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.*;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Set Region With Bad Sk")
@RunWith(Parameterized.class)
@Features("Region")
@Stories("Set Region With Bad Sk")
public class SetRegionWithBadSkTest {

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
    private final String retpath;
    private final Authorized authorized;
    private final ClientSteps userClient;
    private final RegionSteps userRegion;

    private String actualRegionId;

    public SetRegionWithBadSkTest(Domain domain, Region region, Authorized authorized, String retpath) {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.region = region;
        this.authorized = authorized;
        this.retpath = retpath;
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
    @Stories("Set Region With No sk")
    public void regionNotSetWithoutSk() {
        userRegion.setRegionWithWrongSk(region, nullSk(), retpath);
        userRegion.shouldSeeRegionId(anyOf(equalTo(actualRegionId), nullValue()));
    }

    @Test
    @Stories("Set Region With Empty sk")
    public void regionNotSetWithEmptySk() {
        userRegion.setRegionWithWrongSk(region, empty(), retpath);
        userRegion.shouldSeeRegionId(anyOf(equalTo(actualRegionId), nullValue()));
    }

    @Test
    @Stories("Set Region With Sk without first letter")
    public void regionNotSetWithoutFirstLetterOfSk() {
        userRegion.setRegionWithWrongSk(region, withoutFirstLetter(domain, client), retpath);
        userRegion.shouldSeeRegionId(anyOf(equalTo(actualRegionId), nullValue()));
    }

    @Test
    @Stories("Set Region With Random sk")
    public void regionNotSetWithRandomSk() {
        userRegion.setRegionWithWrongSk(region, random(domain, client), retpath);
        userRegion.shouldSeeRegionId(anyOf(equalTo(actualRegionId), nullValue()));
    }
}
