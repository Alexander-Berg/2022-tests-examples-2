package ru.yandex.autotests.mordabackend.mobile.application;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.application.AppItem;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ApplicationParameterProvider;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ApplicationEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.ArrayList;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.selectFirst;
import static java.lang.Integer.parseInt;
import static java.lang.String.valueOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.APPLICATION;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.BROWSERDESC;
import static ru.yandex.autotests.mordabackend.mobile.application.ApplicationUtils.APPLICATION_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.mobile.application.ApplicationUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.mobile.application.ApplicationUtils.PLATFORM_TYPES;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.attach;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 20.08.2014
 */
@Aqua.Test(title = "Mobile Application Items")
@Features("Mobile")
@Stories("Application Items")
@RunWith(CleanvarsParametrizedRunner.class)
public class ApplicationBlockItemsTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}, {6}")
    public static ParametersUtils parameters =
            parameters(APPLICATION_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(new ArrayList<>(PLATFORM_TYPES.keySet()))
                    .withParameterProvider(new ApplicationParameterProvider())
                    .withCleanvarsBlocks(BROWSERDESC, APPLICATION);


    private Language language;
    private Client client;
    private Cleanvars cleanvars;
    private ApplicationEntry expectedEntry;
    private AppItem actualEntry;

    public ApplicationBlockItemsTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                                     Region region, Language language, UserAgent userAgent,
                                     String entryName, ApplicationEntry entry) {
        this.cleanvars = cleanvars;
        this.client = client;
        this.language = language;
        this.expectedEntry = entry;
    }

    @Before
    public void setUp() {
        this.actualEntry = selectFirst(cleanvars.getApplication().getList(),
                having(on(AppItem.class).getId(), equalTo(expectedEntry.getId())));
        attach(actualEntry);
    }

    @Test
    public void applicationItem() throws IOException {

        String url = expectedEntry.getUrl();
        shouldMatchTo(actualEntry, allOfDetailed(
                hasPropertyWithValue(on(AppItem.class).getDomain(), equalTo(expectedEntry.getDomain())),
                hasPropertyWithValue(on(AppItem.class).getLang(), equalTo(expectedEntry.getLang())),
                hasPropertyWithValue(on(AppItem.class).getGeos(), equalTo(expectedEntry.getGeos())),
                hasPropertyWithValue(on(AppItem.class).getPlatform(), equalTo(expectedEntry.getPlatform())),
                hasPropertyWithValue(on(AppItem.class).getUrl(), startsWith(url.replaceAll("//$", ""))),
                hasPropertyWithValue(on(AppItem.class).getIcon(), equalTo(expectedEntry.getIcon())),
                hasPropertyWithValue(on(AppItem.class).getTitle(), equalTo(expectedEntry.getTitle())),
                hasPropertyWithValue(on(AppItem.class).getWeight(),
                        actualEntry.getIspromo() == 0
                                ? equalTo(expectedEntry.getWeight())
                                : equalTo(valueOf(parseInt(expectedEntry.getWeight()) + 1000)))
        ));
        shouldHaveResponseCode(client, normalizeUrl(actualEntry.getIcon()), equalTo(200));
    }

}
