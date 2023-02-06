package ru.yandex.autotests.morda.tests.tv.cleanvars;

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
@Features({MordaTestTags.CLEANVARS, MordaTestTags.TV})
@RunWith(Parameterized.class)
public class TvSchemaTest extends AbstractCleanvarsSchemaTest {
    private static final String TOUCH_JSON_SCHEMA_FILE = "/cleanvars/tv/touch/tv.json";
    private static final String DESKTOP_JSON_SCHEMA_FILE = "/cleanvars/tv/desktop/tv.json";
    private static final String TV_BLOCK = "TV";

    public TvSchemaTest(Morda<?> morda, String jsonSchemaFile) {
        super(morda, jsonSchemaFile, TV_BLOCK);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return getMordas(DESKTOP_JSON_SCHEMA_FILE, TOUCH_JSON_SCHEMA_FILE);
    }
}
