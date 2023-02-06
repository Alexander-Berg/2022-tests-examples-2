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
import java.io.IOException;
import java.text.ParseException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeThat;
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
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;


/**
 * User: ivannik
 * Date: 09.07.2014
 */
@Aqua.Test(title = "Disaster")
@Features("Disaster")
@Stories("Disaster")
@RunWith(CleanvarsParametrizedRunner.class)
public class DisasterTest {
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

    public DisasterTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
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
        assumeTrue("Проверяем только если дизастер", disasterV12Entry != null);
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getProcessed(), equalTo(1)));
    }

    @Test
    public void langParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getLang(),
                equalTo(disasterV12Entry.getLang())));
    }

    @Test
    public void fromParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getFrom(),
                equalTo(disasterV12Entry.getFrom())));
    }

    @Test
    public void tillParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getTill(),
                equalTo(disasterV12Entry.getTill())));
    }

    @Test
    public void textParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getText(),
                equalTo(disasterV12Entry.getText())));
    }

    @Test
    public void titleParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getTitle(),
                equalTo(disasterV12Entry.getTitle())));
    }

    @Test
    public void geosParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getGeos(),
                equalTo(disasterV12Entry.getGeos())));
    }

    @Test
    public void counterParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getCounter(),
                equalTo(disasterV12Entry.getCounter())));
    }

    @Test
    public void domainParameter() {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getDomain(),
                equalTo(disasterV12Entry.getDomain())));
    }

    @Test
    public void popupParameter() {
        assumeThat(disasterV12Entry.getPopupFlag(), equalTo(1));
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getPopupFlag(), equalTo(1)));
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getPopup(), equalTo("popup")));
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getPopupText(),
                not(isEmptyOrNullString())));
    }

    @Test
    public void linkParameter() throws IOException {
        assumeThat(disasterV12Entry.getLink(), not(equalTo("popup")));
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getLink(),
                equalTo(disasterV12Entry.getLink())));
        assumeThat(disasterV12Entry.getLink(), not(isEmptyOrNullString()));
        shouldHaveResponseCode(client, cleanvars.getDisaster().getLink(), userAgent, equalTo(200));
    }

    @Test
    public void noPromoParameter() throws IOException {
        shouldHaveParameter(cleanvars.getDisaster(), having(on(Disaster.class).getNoPromo(),
                equalTo(disasterV12Entry.getNoPromo())));
    }

}
