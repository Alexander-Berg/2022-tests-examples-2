package ru.yandex.autotests.mordabackend.example;

import org.junit.Ignore;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.example.Example;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isIn;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock.SMARTEXAMPLE;
import static ru.yandex.autotests.mordabackend.example.SearchExampleUtils.EXAMPLES_SOURCE_EXPORTS;
import static ru.yandex.autotests.mordabackend.example.SearchExampleUtils.EXAMPLE_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.example.SearchExampleUtils.LANGUAGES;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.WP8;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;

/**
 * User: ivannik
 * Date: 05.08.2014
 */
@Aqua.Test(title = "Search Example")
@Features("Search Example")
@Stories("Search Example")
@Ignore("Need wp page with ?q=, cant do that now")
@RunWith(CleanvarsParametrizedRunner.class)
public class SearchExampleTest {


    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(EXAMPLE_REGIONS_ALL)
                    .withLanguages(LANGUAGES)
                    .withUserAgents(WP8)
                    .withCleanvarsBlocks(SMARTEXAMPLE);


    private Example example;

    public SearchExampleTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                           Language language, UserAgent userAgent) {
        this.example = cleanvars.getSmartExample();
    }

    @Test
    public void id() {
        shouldHaveParameter(example, having(on(Example.class).getId(), notNullValue()));
    }

    @Test
    public void text() {
        shouldHaveParameter(example, having(on(Example.class).getText(), notNullValue()));
    }

    @Test
    public void source() {
        shouldHaveParameter(example, having(on(Example.class).getSource(), isIn(EXAMPLES_SOURCE_EXPORTS)));
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(example, having(on(Example.class).getShow(), equalTo(1)));
    }

    @Test
    public void processedFlag() {
        shouldHaveParameter(example, having(on(Example.class).getProcessed(), equalTo(1)));
    }
}
