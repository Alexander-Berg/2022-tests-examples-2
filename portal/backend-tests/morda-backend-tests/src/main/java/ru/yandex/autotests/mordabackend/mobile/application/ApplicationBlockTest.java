package ru.yandex.autotests.mordabackend.mobile.application;

import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.application.AppItem;
import ru.yandex.autotests.mordabackend.beans.application.Application;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.ApplicationEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.APPLICATION;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.BROWSERDESC;
import static ru.yandex.autotests.mordabackend.mobile.application.ApplicationUtils.APPLICATION_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.mobile.application.ApplicationUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.mobile.application.ApplicationUtils.PLATFORM_TYPES;
import static ru.yandex.autotests.mordabackend.mobile.application.ApplicationUtils.getTitle;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.attach;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.parameters.ApplicationParameterProvider.getApplications;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: ivannik
 * Date: 20.08.2014
 */
@Aqua.Test(title = "Mobile Application")
@Features("Mobile")
@Stories("Application")
@RunWith(CleanvarsParametrizedRunner.class)
public class ApplicationBlockTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(APPLICATION_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(new ArrayList<>(PLATFORM_TYPES.keySet()))
                    .withCleanvarsBlocks(BROWSERDESC, APPLICATION);


    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;

    public ApplicationBlockTest(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                                Region region, Language language, UserAgent userAgent) {
        this.language = language;
        this.cleanvars = cleanvars;
        this.region = region;
        this.userAgent = userAgent;
        attach(cleanvars.getApplication());
    }

    @Test
    public void title() {
        shouldHaveParameter(cleanvars.getApplication(), having(on(Application.class).getTitle(),
                equalTo(getTitle(language, cleanvars.getBrowserDesc()))));
    }

    @Test
    public void showFlag() {
        List<String> expectedItems = extract(
                getApplications(region, language, userAgent),
                on(ApplicationEntry.class).getId());

        if(expectedItems.size() == 0){
            shouldHaveParameter(cleanvars.getApplication(), having(on(Application.class).getShow(), equalTo(0)));

        } else{
            shouldHaveParameter(cleanvars.getApplication(), having(on(Application.class).getShow(), equalTo(1)));

        }
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(cleanvars.getApplication(), having(on(Application.class).getProcessed(), equalTo(1)));
    }

    @Test
    public void applicationItemsList() {
        List<String> expectedItems = extract(
                getApplications(region, language, userAgent),
                on(ApplicationEntry.class).getId());
        List<String> actualItems = extract(
                cleanvars.getApplication().getList(),
                on(AppItem.class).getId());

        shouldMatchTo(actualItems, hasSameItemsAsCollection(expectedItems));
    }

}
