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

import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.*;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Change Region With Bad Sk")
@RunWith(Parameterized.class)
@Features("Region")
@Stories("Change Region With Bad Sk")
public class ChangeRegionWithBadSkTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Region: \"{1}\" -> \"{2}\"; Retpath: {3}")
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

    public ChangeRegionWithBadSkTest(Domain domain, Region region1, Region region2, Authorized authorized, String retpath) {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.region1 = region1;
        this.region2 = region2;
        this.authorized = authorized;
        this.retpath = retpath;
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
    @Stories("Change Region With No sk")
    public void regionNotChangedWithoutSk() {
        userRegion.setRegionWithWrongSk(region2, nullSk(), retpath);
        userRegion.shouldSeeRegionId(region1.getRegionId());
    }

    @Test
    @Stories("Change Region With Empty sk")
    public void regionNotChangedWithEmptySk() {
        userRegion.setRegionWithWrongSk(region2, empty(), retpath);
        userRegion.shouldSeeRegionId(region1.getRegionId());
    }

    @Test
    @Stories("Change Region With Sk without first letter")
    public void regionNotChangedWithoutFirstLetterOfSk() {
        userRegion.setRegionWithWrongSk(region2, withoutFirstLetter(domain, client), retpath);
        userRegion.shouldSeeRegionId(region1.getRegionId());
    }

    @Test
    @Stories("Change Region With Random sk")
    public void regionNotChangedWithRandomSk() {
        userRegion.setRegionWithWrongSk(region2, random(domain, client), retpath);
        userRegion.shouldSeeRegionId(region1.getRegionId());
    }
}
