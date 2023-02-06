package ru.yandex.autotests.morda.tests.geo.cleanvars;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.main.DesktopFamilyMainMorda;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.tests.AbstractCleanvarsSchemaTest;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * User: asamar
 * Date: 15.02.17
 */
@Aqua.Test(title = MordaTestTags.SCHEMA)
@Features({MordaTestTags.CLEANVARS, MordaTestTags.GEO})
@RunWith(Parameterized.class)
public class GeoSchemaTest extends AbstractCleanvarsSchemaTest {
    private static final String DESKTOP_JSON_SCHEMA_FILE = "/cleanvars/geo/desktop/geo.json";
    private static final String GEO_BLOCK = "Geo";


    public GeoSchemaTest(Morda<?> morda, String jsonSchemaFile) {
        super(morda, jsonSchemaFile, GEO_BLOCK);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Object[]> reqs = new ArrayList<>();
        List<Morda<?>> desktopMordas = new ArrayList<>();

        desktopMordas.addAll(DesktopMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));
        desktopMordas.addAll(DesktopFamilyMainMorda.getDefaultList(CONFIG.pages().getEnvironment()));

        desktopMordas.forEach(morda ->
                reqs.add(new Object[]{morda, DESKTOP_JSON_SCHEMA_FILE})
        );

        return reqs;
    }
}
