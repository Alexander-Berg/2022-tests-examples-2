package ru.yandex.autotests.mordabackend.etrains;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.etrains.Etrains;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.ETRAINS;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ATBASAR;
import static ru.yandex.autotests.utils.morda.region.Region.BROVARY;
import static ru.yandex.autotests.utils.morda.region.Region.ORSHA;
import static ru.yandex.autotests.utils.morda.region.Region.VYBORG;

/**
 * User: ivannik
 * Date: 10.09.2014
 */
@Aqua.Test(title = "Etrains Block")
@Features("Etrains")
@Stories("Etrains Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class EtrainsTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(VYBORG, BROVARY, ORSHA, ATBASAR)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(FF_34, TOUCH)
                    .withCleanvarsBlocks(ETRAINS);

    private final Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;

    public EtrainsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                      Region region, Language language, UserAgent userAgent) {
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.client = client;
        this.cleanvars = cleanvars;
    }

    @Test
    public void href() throws IOException {
        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getHref(), not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, normalizeUrl(cleanvars.getEtrains().getHref()), userAgent, equalTo(200));
        shouldHaveParameter(cleanvars.getEtrains(),
                having(on(Etrains.class).getHrefBack(), not(isEmptyOrNullString())));
        shouldHaveResponseCode(client, normalizeUrl(cleanvars.getEtrains().getHrefBack()), userAgent, equalTo(200));
    }

    @Test
    public void raspHost() throws IOException {
        shouldHaveParameter(cleanvars.getEtrains(),
                having(on(Etrains.class).getRaspHost(), not(isEmptyOrNullString())));
        addLink(cleanvars.getEtrains().getRaspHost(), region, false, language, userAgent);
        shouldHaveResponseCode(client, normalizeUrl(cleanvars.getEtrains().getRaspHost()), userAgent, equalTo(200));
        shouldHaveParameter(cleanvars.getEtrains(),
                having(on(Etrains.class).getRaspHostBigRu(), not(isEmptyOrNullString())));
        shouldHaveResponseCode(client,
                normalizeUrl(cleanvars.getEtrains().getRaspHostBigRu()), userAgent, equalTo(200));
    }

    @Test
    public void cstname() {
        shouldHaveParameter(cleanvars.getEtrains(),
                having(on(Etrains.class).getCstname(), not(isEmptyOrNullString())));
    }

    @Test
    public void stname() {
        shouldHaveParameter(cleanvars.getEtrains(),
                having(on(Etrains.class).getStname(), not(isEmptyOrNullString())));
    }

    @Test
    public void scheduleFlag() {
        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getSchedule(), equalTo(1)));
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getEtrains(), having(on(Etrains.class).getProcessed(), equalTo(1)));
    }
}
