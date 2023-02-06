package ru.yandex.autotests.mordabackend.mobile.rasp;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.rasp.Rasp;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.RaspEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isOneOf;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.RASP;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.ANDROID_HTC_SENS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.attach;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.geo;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.EKATERINBURG;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.LYUDINOVO;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.region.Region.NIZHNIY_NOVGOROD;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;

/**
 * User: ivannik
 * Date: 22.08.2014
 */
@Aqua.Test(title = "Rasp Mobile")
@Features("Mobile")
@Stories("Rasp Mobile")
@RunWith(CleanvarsParametrizedRunner.class)
public class RaspBlockTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(SANKT_PETERBURG, MOSCOW, KIEV, HARKOV, MINSK, ASTANA, NIZHNIY_NOVGOROD, EKATERINBURG, LYUDINOVO)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(TOUCH, WP8, ANDROID_HTC_SENS)
                    .withCleanvarsBlocks(RASP);

    private Client client;
    private UserAgent userAgent;
    private Cleanvars cleanvars;
    private RaspEntry expectedEntry;

    public RaspBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                         Language language, UserAgent userAgent) {
        this.client = client;
        this.userAgent = userAgent;
        this.cleanvars = cleanvars;
        this.expectedEntry = export(MordaExports.RASP, geo(region.getRegionIdInt()));
        attach(cleanvars.getRasp());
    }

    @Test
    public void raspItems() {
        shouldHaveParameter(cleanvars.getRasp(), allOfDetailed(
                hasPropertyWithValue(on(Rasp.class).getAero(), isOneOf(1, 0)),
                hasPropertyWithValue(on(Rasp.class).getBus(), isOneOf(1, 0)),
                hasPropertyWithValue(on(Rasp.class).getEl(), isOneOf(1, 0)),
                hasPropertyWithValue(on(Rasp.class).getShip(), isOneOf(1, 0)),
                hasPropertyWithValue(on(Rasp.class).getTrain(), isOneOf(1, 0)),
                hasPropertyWithValue(on(Rasp.class).getShow(), equalTo(1)),
                hasPropertyWithValue(on(Rasp.class).getProcessed(), equalTo(1))
        ));
    }
}
