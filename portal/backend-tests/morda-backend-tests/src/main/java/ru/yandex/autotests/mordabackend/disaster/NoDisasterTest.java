package ru.yandex.autotests.mordabackend.disaster;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.disaster.Disaster;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.DisasterV12Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.text.ParseException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.DISASTER;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.HIDDENTIME;
import static ru.yandex.autotests.mordabackend.disaster.DisasterUtils.DISASTER_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.disaster.DisasterUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.disaster.DisasterUtils.getDisasterEntry;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;


/**
 * User: ivannik
 * Date: 09.07.2014
 */
@Aqua.Test(title = "No Disaster")
@Features("Disaster")
@Stories("No Disaster")
@RunWith(CleanvarsParametrizedRunner.class)
public class NoDisasterTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(DISASTER_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(DISASTER, HIDDENTIME);

    private Client client;
    private Cleanvars cleanvars;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private DisasterV12Entry disasterV12Entry;

    public NoDisasterTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                          Language language, UserAgent userAgent) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
    }

    @Before
    public void setUp() throws ParseException {
        this.disasterV12Entry = getDisasterEntry(region, language, userAgent, cleanvars.getHiddenTime());
        assumeTrue("Проверяем только не должно быть дизастера", disasterV12Entry == null);
    }

    @Test
    public void showParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getShow(), equalTo(0)));
    }

    @Test
    public void processedParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getProcessed(), equalTo(1)));
    }
}
