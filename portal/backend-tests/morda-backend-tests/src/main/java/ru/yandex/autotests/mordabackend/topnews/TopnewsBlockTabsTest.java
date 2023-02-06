package ru.yandex.autotests.mordabackend.topnews;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.topnews.MobileLinks;
import ru.yandex.autotests.mordabackend.beans.topnews.Topnews;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsTab;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.text.ParseException;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.*;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.*;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.TOPNEWS_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.topnews.TopnewsUtils.getNewsTabsMatcher;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.Language.*;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff
 * Date: 20.06.2014
 */
@Aqua.Test(title = "Topnews Block Tabs")
@Features("Topnews")
@Stories("Topnews Block Tabs")
@RunWith(CleanvarsParametrizedRunner.class)
public class TopnewsBlockTabsTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(TOPNEWS_REGIONS_ALL)
                    .withLanguages(RU, UK, BE, KK, TT)
                    .withUserAgents(FF_34, PDA, TOUCH)
                    .withCleanvarsBlocks(TOPNEWS, LOCAL, HIDDENTIME);

    private final Cleanvars cleanvars;
    private final Region region;
    private final UserAgent userAgent;

    public TopnewsBlockTabsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                Language language, UserAgent userAgent) {
        this.cleanvars = cleanvars;
        this.region = region;
        this.userAgent = userAgent;
    }

    @Test
    public void defaultTabIndex() throws IOException, ParseException {
        shouldHaveParameter(cleanvars.getTopnews(),
                having(on(Topnews.class).getDefaultTabIndex(), equalTo(0)));
    }

    @Test
    public void tabsAreSameAsTabsHash() throws IOException, ParseException {
        shouldHaveParameter(cleanvars.getTopnews(),
                having(on(Topnews.class).getTabs(), hasItems(cleanvars.getTopnews().getTabshash().values().toArray())));
        shouldHaveParameter(cleanvars.getTopnews(),
                having(on(Topnews.class).getTabs(), hasSize(cleanvars.getTopnews().getTabshash().values().size())));
    }

    @Test
    public void newsTabsAndLinks() throws IOException, ParseException {
        assumeThat("Должен быть не турецкий домен", region.getDomain(), not(COM_TR));
        List<String> keys;
        if (userAgent.equals(PDA)) {
            keys = extract(cleanvars.getTopnews().getMobileLinks(), on(MobileLinks.class).getId());
        } else {
            keys = extract(cleanvars.getTopnews().getTabs(), on(TopnewsTab.class).getKey());
        }
        shouldMatchTo(keys, getNewsTabsMatcher(region, userAgent));
    }
}
