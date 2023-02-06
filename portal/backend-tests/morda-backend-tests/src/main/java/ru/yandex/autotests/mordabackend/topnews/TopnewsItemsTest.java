package ru.yandex.autotests.mordabackend.topnews;

import org.junit.Ignore;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTabItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.NewsItemsParameterProvider;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.TOPNEWS;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.TOPNEWS_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.getNewsItemHrefMatcher;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.getNewsLanguageMatcher;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.PDA;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.TOUCH;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TT;
import static ru.yandex.autotests.utils.morda.language.Language.UK;

/**
 * User: eoff
 * Date: 20.06.2014
 */
@Aqua.Test(title = "News Items")
@Features("Topnews")
@Stories("News Items")
@RunWith(CleanvarsParametrizedRunner.class)
public class TopnewsItemsTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {7}: {8}")
    public static ParametersUtils parameters =
            parameters(TOPNEWS_REGIONS_ALL)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withParameterProvider(new NewsItemsParameterProvider())
                    .withCleanvarsBlocks(TOPNEWS);

    private final Client client;
    private final Cleanvars cleanvars;
    private final Region region;
    private final Language language;
    private final UserAgent userAgent;
    private final ServicesV122Entry servicesV122Entry;
    private final TopnewsTabItem newsTabItem;

    public TopnewsItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                            Language language, UserAgent userAgent, ServicesV122Entry servicesV122Entry, String key,
                            int i, TopnewsTabItem newsTabItem) {
        this.client = client;
        this.cleanvars = cleanvars;
        this.region = region;
        this.language = language;
        this.userAgent = userAgent;
        this.servicesV122Entry = servicesV122Entry;
        this.newsTabItem = newsTabItem;
    }

    @Test
    @Ignore
    public void newsItemHrefText() throws IOException {
        shouldHaveParameter(newsTabItem, having(on(TopnewsTabItem.class).getHreftext(), not(isEmptyOrNullString())));
        shouldHaveParameter(newsTabItem, having(on(TopnewsTabItem.class).getHreftext(),
                getNewsLanguageMatcher(region, language)));
    }

    @Test
    @Ignore
    public void newsItemText() throws IOException {
        shouldHaveParameter(newsTabItem, having(on(TopnewsTabItem.class).getText(), not(isEmptyOrNullString())));
        shouldHaveParameter(newsTabItem, having(on(TopnewsTabItem.class).getText(),
                getNewsLanguageMatcher(region, language)));
    }

    @Test
    public void newsItemHref() throws IOException {
        shouldHaveParameter(newsTabItem, having(on(TopnewsTabItem.class).getHref(),
                getNewsItemHrefMatcher(servicesV122Entry, userAgent, region)));
        shouldHaveResponseCode(client, newsTabItem.getHref(), userAgent, equalTo(200));
    }
}
