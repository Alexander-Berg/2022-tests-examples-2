package ru.yandex.autotests.morda.tests.afisha.searchapi.v1;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.v1.SearchApiV1Request;
import ru.yandex.autotests.morda.tests.AbstractSchemaTest;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = MordaTestTags.AFISHA)
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V1, MordaTestTags.AFISHA})
@RunWith(Parameterized.class)
public class AfishaV1SchemaTest extends AbstractSchemaTest {
    private static final String JSON_SCHEMA_FILE = "/api/search/1/afisha/afisha-response.json";

    public AfishaV1SchemaTest(SearchApiV1Request request) {
        super(request, JSON_SCHEMA_FILE);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiV1Request> data() {
        return AfishaV1TestCases.getData(CONFIG.pages().getEnvironment());
    }
}
