package ru.yandex.autotests.mordabackend.logo;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.logo.Logo;
import ru.yandex.autotests.mordabackend.utils.parameters.LogoParameterProvider;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.LogoV14Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.text.ParseException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.*;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.HIDDENTIME;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.LOGO;
import static ru.yandex.autotests.mordabackend.logo.LogoUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.logo.LogoUtils.LOGO_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 14.07.2014
 */
@Aqua.Test(title = "Special Logotype")
@Features("Logotype")
@Stories("Special Logotype")
@RunWith(CleanvarsParametrizedRunner.class)
public class SpecialLogoTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}")
    public static ParametersUtils parameters =
            parameters(LOGO_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withParameterProvider(new LogoParameterProvider())
                    .withCleanvarsBlocks(LOGO, HIDDENTIME);

    private Client client;
    private Cleanvars cleanvars;
    private Region region;
    private Language language;
    private LogoV14Entry logoEntry;

    public SpecialLogoTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                           Language language, LogoV14Entry logoEntry) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.logoEntry = logoEntry;
    }

    @Before
    public void setUp() {
        assumeThat("Специального лого нет", logoEntry, not(nullValue()));
    }

    @Test
    public void processedFlag() throws ParseException {
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getProcessed(), equalTo(1)));
    }

    @Test
    public void animateParameter() throws ParseException {
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getAnimate(), equalTo(logoEntry.getAnimate())));
    }

    @Test
    public void titleParameter() throws ParseException {
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getTitle(), equalTo(logoEntry.getTitle())));
    }

    @Test
    public void hrefParameter() throws ParseException {
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getHref(), equalTo(logoEntry.getHref())));
    }


    @Test
    public void urlParameter() throws ParseException {
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getUrl(), equalTo(logoEntry.getUrl())));
    }

    @Test
    public void counterParameter() throws ParseException {
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getCounter(), equalTo(logoEntry.getCounter())));
    }

    @Test
    public void playerParameter() throws ParseException {
        String player = logoEntry.getPlayer();
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getPlayer(), equalTo(player)));
    }

    @Test
    public void voffsetParameter() throws ParseException {
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getVoffset(), equalTo(logoEntry.getVoffset())));
    }

    @Test
    public void hoffsetParameter() throws ParseException {
        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getHoffset(), equalTo(logoEntry.getHoffset())));
    }

    @Test
    public void geosParameter() throws ParseException {
//        shouldHaveParameter(cleanvars.getLogo(), having(on(Logo.class).getGeos(),
//                isIn(logoEntry.getGeos().split(", "))));
    }
}