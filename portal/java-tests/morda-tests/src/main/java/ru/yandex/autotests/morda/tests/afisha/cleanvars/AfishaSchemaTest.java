package ru.yandex.autotests.morda.tests.afisha.cleanvars;

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
 * Date: 13.02.17
 */
@Aqua.Test(title = MordaTestTags.SCHEMA)
@Features({MordaTestTags.CLEANVARS, MordaTestTags.AFISHA})
@RunWith(Parameterized.class)
public class AfishaSchemaTest extends AbstractCleanvarsSchemaTest {
    private static final String TOUCH_JSON_SCHEMA_FILE = "/cleanvars/afisha/touch/afisha.json";
    private static final String DESKTOP_JSON_SCHEMA_FILE = "/cleanvars/afisha/desktop/afisha.json";
    private static final String AFISHA_BLOCK = "Afisha";

    public AfishaSchemaTest(Morda<?> morda, String schemaFile) {
        super(morda, schemaFile, AFISHA_BLOCK);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return getMordas(DESKTOP_JSON_SCHEMA_FILE, TOUCH_JSON_SCHEMA_FILE);
    }

}
