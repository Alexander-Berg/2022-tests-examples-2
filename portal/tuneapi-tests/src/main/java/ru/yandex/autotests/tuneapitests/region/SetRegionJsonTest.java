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
import ru.yandex.autotests.tuneclient.TuneResponse;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.nullValue;
import static org.junit.Assume.assumeTrue;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Set Region Json")
@RunWith(Parameterized.class)
@Features("Region")
@Stories("Set Region Json")
public class SetRegionJsonTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Region: \"{1}\"; {2}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Region r : Region.values()) {
                for (Authorized auth : Authorized.values()) {
                    data.add(new Object[]{d, r, auth});
                }
            }
        }
        return data;
    }

    private final Client client;
    private final Domain domain;
    private final Region region;
    private final Authorized authorized;
    private final ClientSteps userClient;
    private final RegionSteps userRegion;

    private String actualRegionId;

    public SetRegionJsonTest(Domain domain, Region region, Authorized authorized) {
        this.domain = domain;
        this.region = region;
        this.authorized = authorized;
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
    @Stories("Set Region Json")
    public void setRegionJson() {
        assumeTrue("Domain is invalid", domain.isDomainValidForJsonRequest());
        TuneResponse response = userRegion.setRegionJson(region, "1");
        userClient.shouldSeeOkTuneResponse(response);
        userRegion.shouldSeeRegionId(region.getRegionId());
    }

    @Test
    @Stories("Error Region Json With Invalid Domain")
    public void errorRegionJson() {
        assumeTrue("Domain is valid", !domain.isDomainValidForJsonRequest());
        TuneResponse response = userRegion.setRegionJson(region, "1");
        userClient.shouldSeeErrorTuneResponse(response);
        userRegion.shouldSeeRegionId(anyOf(equalTo(actualRegionId), nullValue()));
    }

    @Test
    @Stories("Error Region Json Without Sk")
    public void errorRegionJsonWithoutSk() {
        TuneResponse response = userRegion.setRegionJsonWithoutSk(region, "1");
        userClient.shouldSeeErrorTuneResponse(response);
        userRegion.shouldSeeRegionId(anyOf(equalTo(actualRegionId), nullValue()));
    }

    @Test
    @Stories("Set Region Json On Tune Internal")
    public void setRegionOnTuneInternal() {
        TuneResponse response = userRegion.setRegionJsonOnTuneInternal(region, null);
        userClient.shouldSeeOkTuneResponse(response);
        userRegion.shouldSeeRegionId(region.getRegionId());
    }

}
