package ru.yandex.autotests.morda.tests.traffic.cleanvars;

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

import static ru.yandex.geobase.regions.Kazakhstan.ALMATY;

/**
 * User: asamar
 * Date: 15.02.17
 */
@Aqua.Test(title = MordaTestTags.SCHEMA)
@Features({MordaTestTags.CLEANVARS, MordaTestTags.TRAFFIC})
@RunWith(Parameterized.class)
public class TrafficSchemaTest extends AbstractCleanvarsSchemaTest {
    private static final String TOUCH_JSON_SCHEMA_FILE = "/cleanvars/traffic/touch/traffic.json";
    private static final String DESKTOP_JSON_SCHEMA_FILE = "/cleanvars/traffic/desktop/traffic.json";
    private static final String TRAFFIC_BLOCK = "Traffic";

    public TrafficSchemaTest(Morda<?> morda, String jsonSchemaFile) {
        super(morda, jsonSchemaFile, TRAFFIC_BLOCK);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {

        return getMordas(DESKTOP_JSON_SCHEMA_FILE, TOUCH_JSON_SCHEMA_FILE).stream()
                .filter(e ->((MainMorda<?>)e[0]).getRegion() != ALMATY)
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
}
