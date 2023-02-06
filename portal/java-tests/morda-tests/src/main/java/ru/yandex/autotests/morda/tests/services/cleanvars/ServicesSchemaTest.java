package ru.yandex.autotests.morda.tests.services.cleanvars;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.autotests.morda.tests.AbstractCleanvarsSchemaTest;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;

import static ru.yandex.autotests.morda.pages.MordaDomain.RU;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_MAIN;

/**
 * User: asamar
 * Date: 15.02.17
 */
@Aqua.Test(title = MordaTestTags.SCHEMA)
@Features({MordaTestTags.CLEANVARS, MordaTestTags.SERVICES})
@RunWith(Parameterized.class)
public class ServicesSchemaTest extends AbstractCleanvarsSchemaTest{
    private static final String TOUCH_JSON_SCHEMA_FILE = "/cleanvars/services/touch/services.json";
    private static final String DESKTOP_JSON_SCHEMA_FILE = "/cleanvars/services/desktop/services.json";
    private static final String SERVICES_BLOCK = "Services";

    public ServicesSchemaTest(Morda<?> morda, String jsonSchemaFile) {
        super(morda, jsonSchemaFile, SERVICES_BLOCK);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return getMordas(DESKTOP_JSON_SCHEMA_FILE, TOUCH_JSON_SCHEMA_FILE).stream()
                .filter(e -> !(((MainMorda<?>)e[0]).getMordaType() == TOUCH_MAIN &&
                        ((MainMorda<?>)e[0]).getDomain() != RU))
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
}
