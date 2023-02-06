package ru.yandex.autotests.mordabackend.topnews;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.topnews.Topnews;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.parameters.ServicesV122ParameterProvider;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.text.ParseException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.*;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.*;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.Language.*;

/**
 * User: eoff
 * Date: 20.06.2014
 */
@Aqua.Test(title = "Topnews Block")
@Features("Topnews")
@Stories("Topnews Block")
@RunWith(CleanvarsParametrizedRunner.class)
public class TopnewsBlockTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(TOPNEWS_REGIONS_ALL)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withParameterProvider(new ServicesV122ParameterProvider("news"))
                    .withCleanvarsBlocks(TOPNEWS, LOCAL, HIDDENTIME);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final Language language;
    private final UserAgent userAgent;
    private final ServicesV122Entry servicesV122Entry;

    public TopnewsBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                            Language language, UserAgent userAgent, ServicesV122Entry servicesV122Entry) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.servicesV122Entry = servicesV122Entry;
    }

    @Test
    public void topnewsHref() throws IOException {
        shouldHaveParameter(cleanvars.getTopnews(),
                having(on(Topnews.class).getHref(), getTopnewsHrefMatcher(region, servicesV122Entry, userAgent)));
        addLink(cleanvars.getTopnews().getHref(), region, false, language, userAgent);
        shouldHaveResponseCode(client, cleanvars.getTopnews().getHref(), userAgent, equalTo(200));
    }

    @Test
    public void showFlag() throws IOException {
        shouldHaveParameter(cleanvars.getTopnews(),
                having(on(Topnews.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() throws IOException {
        shouldHaveParameter(cleanvars.getTopnews(),
                having(on(Topnews.class).getProcessed(), equalTo(1)));
    }

    @Test
    public void numbers() throws IOException {
        shouldHaveParameter(cleanvars.getTopnews(),
                having(on(Topnews.class).getNumbers().getShow(), equalTo(1)));
    }

    @Test
    public void topnewsDateTimeFields() throws IOException, ParseException {
        shouldHaveParameter(cleanvars.getTopnews(), allOf(
                having(on(Topnews.class).getFulltime(), getFullTimeMatcher(cleanvars.getHiddenTime())),
                having(on(Topnews.class).getTime(), getTimeMatcher(cleanvars.getHiddenTime()))
        ));
    }

    @Test
    public void topnewsMobileDateTimeFields() throws IOException, ParseException {
        assumeFalse("Дата/время не отображаются на мобильной", userAgent.isMobile());
        shouldHaveParameter(cleanvars.getTopnews(), allOf(
                having(on(Topnews.class).getBigWday(), getWDayMatcher(cleanvars.getLocal(), language)),
                having(on(Topnews.class).getBigMonth(), getMonthMatcher(cleanvars.getLocal(), language))
        ));
    }
}
