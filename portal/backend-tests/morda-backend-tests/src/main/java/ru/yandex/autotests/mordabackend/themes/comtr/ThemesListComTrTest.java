package ru.yandex.autotests.mordabackend.themes.comtr;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.themes.Theme;
import ru.yandex.autotests.mordabackend.beans.themes.Themes;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesComtrEntry;
import ru.yandex.autotests.mordaexportslib.ExportProvider;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;

import java.util.Collection;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_COMTR;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */

public class ThemesListComTrTest {
    private static final Properties CONFIG = new Properties();
    private static final Themes THEMES = new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), COM_TR)
            .themeActions().getCatalog().getThemes();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() throws Exception {
        return ParametrizationConverter.convert(extract(ExportProvider.allExports(THEMES_COMTR),
                on(ThemesComtrEntry.class).getId()));
    }

    private String themeId;

    public ThemesListComTrTest(String themeId) {
        this.themeId = themeId;
    }

//    @Test
    public void hasThemeInCleanvarsComTr() {
        assertThat(THEMES.toString(), selectFirst(THEMES.getList(), having(on(Theme.class).getId(), equalTo(themeId))),
                notNullValue());
    }
}
