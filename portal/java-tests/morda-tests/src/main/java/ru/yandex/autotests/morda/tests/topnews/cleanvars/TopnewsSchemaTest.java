package ru.yandex.autotests.morda.tests.topnews.cleanvars;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.tests.AbstractCleanvarsSchemaTest;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

/**
 * User: asamar
 * Date: 15.02.17
 */
@Aqua.Test(title = MordaTestTags.SCHEMA)
@Features({MordaTestTags.CLEANVARS, MordaTestTags.TOPNEWS})
@RunWith(Parameterized.class)
public class TopnewsSchemaTest extends AbstractCleanvarsSchemaTest {
    private static final String TOUCH_JSON_SCHEMA_FILE = "/cleanvars/topnews/touch/topnews.json";
    private static final String DESKTOP_JSON_SCHEMA_FILE = "/cleanvars/topnews/desktop/topnews.json";
    private static final String TOPNEWS_BLOCK = "Topnews";

    public TopnewsSchemaTest(Morda<?> morda, String jsonSchemaFile) {
        super(morda, jsonSchemaFile, TOPNEWS_BLOCK);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return getMordas(DESKTOP_JSON_SCHEMA_FILE, TOUCH_JSON_SCHEMA_FILE);
    }
}
