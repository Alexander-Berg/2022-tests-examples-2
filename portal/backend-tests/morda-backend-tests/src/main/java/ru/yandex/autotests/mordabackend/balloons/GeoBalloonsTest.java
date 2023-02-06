package ru.yandex.autotests.mordabackend.balloons;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.citysuggest.CitySuggest;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.Arrays;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordabackend.MordaClient.getJsonEnabledClient;
import static ru.yandex.autotests.mordabackend.MordaClient.getRemapHostDnsResolver;
import static ru.yandex.autotests.mordabackend.balloons.BalloonsUtils.*;
import static ru.yandex.autotests.mordabackend.beans.citysuggest.SuggestType.*;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.CITY_SUGGEST;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SK;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: ivannik
 * Date: 29.09.2014
 */
//@Aqua.Test(title = "Geo Balloons")
//@Features("Balloons")
//@Stories("Geo Balloons")
//@RunWith(CleanvarsParametrizedRunner.class)
public class GeoBalloonsTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(RU, UA, KZ, BY, COM_TR)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(CITY_SUGGEST);


    private MordaClient mordaClient;
    private UserAgent userAgent;
    private Region region;
    private Client client;

    public GeoBalloonsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                           Region region, UserAgent userAgent) {
        this.mordaClient = mordaClient;
        this.userAgent = userAgent;
        this.region = region;
        this.client = client;
    }

//    @Test
    public void balloon1ThisCity() {

        Client cleanClient =
                getJsonEnabledClient(getRemapHostDnsResolver());
        mordaClient.cleanvarsActions(cleanClient)
                .get(userAgent, NEAR_CAPITAL_REGION_IP.get(region.getDomain()), Arrays.asList(SK));
        Cleanvars cleanvars = mordaClient.cleanvarsActions(cleanClient)
                .get(userAgent, NEAR_CAPITAL_REGION_IP.get(region.getDomain()), Arrays.asList(CITY_SUGGEST));

        shouldHaveParameter(cleanvars.getCitySuggest(), having(on(CitySuggest.class).getType(), equalTo(THIS_CITY)));
        shouldHaveParameter(cleanvars.getCitySuggest(),
                having(on(CitySuggest.class).getCityGid(), equalTo(region.getRegionIdInt())));
        shouldHaveParameter(cleanvars.getCitySuggest(), having(on(CitySuggest.class).getThisGid(), equalTo(0)));
        if (userAgent.isMobile()) {
            shouldHaveParameter(cleanvars.getCitySuggest(), having(on(CitySuggest.class).getOtherCities(), empty()));
        } else {
            shouldHaveParameter(cleanvars.getCitySuggest(),
                    having(on(CitySuggest.class).getOtherCities(), not(empty())));
        }
    }

//    @Test
    public void balloon2LeaveCity() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client)
                .get(userAgent, FAR_FROM_CAPITAL_REGION_IP.get(region.getDomain()), Arrays.asList(CITY_SUGGEST));

        shouldHaveParameter(cleanvars.getCitySuggest(), having(on(CitySuggest.class).getType(), equalTo(LEAVE_CITY)));
        shouldHaveParameter(cleanvars.getCitySuggest(),
                having(on(CitySuggest.class).getCityGid(), equalTo(region.getRegionIdInt())));
        shouldHaveParameter(cleanvars.getCitySuggest(), having(on(CitySuggest.class).getThisGid(), equalTo(0)));
        if (userAgent.isMobile()) {
            shouldHaveParameter(cleanvars.getCitySuggest(), having(on(CitySuggest.class).getOtherCities(), empty()));
        } else {
            shouldHaveParameter(cleanvars.getCitySuggest(),
                    having(on(CitySuggest.class).getOtherCities(), not(empty())));
        }
    }

//    @Test
    public void balloon3OtherCity() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client)
                .get(userAgent, OTHER_CITY_IN_DOMAIN_IP.get(region.getDomain()), Arrays.asList(CITY_SUGGEST));


        shouldHaveParameter(cleanvars.getCitySuggest(),
                having(on(CitySuggest.class).getCityGid(),
                        equalTo(OTHER_CITY_IN_DOMAIN_REGIONS.get(region.getDomain()).getRegionIdInt())));
        shouldHaveParameter(cleanvars.getCitySuggest(), having(on(CitySuggest.class).getType(), equalTo(OTHER_CITY)));
        shouldHaveParameter(cleanvars.getCitySuggest(),
                having(on(CitySuggest.class).getThisGid(), equalTo(region.getRegionIdInt())));
        shouldHaveParameter(cleanvars.getCitySuggest(), having(on(CitySuggest.class).getOtherCities(), empty()));
    }

}
