package ru.yandex.autotests.mordabackend.themes;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.themes.Theme;
import ru.yandex.autotests.mordabackend.beans.themes.Themes;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesEntry;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordabackend.themes.ThemesUtils.getThemes;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: asamar
 * Date: 28.01.16
 */
@Aqua.Test(title = "All Themes")
@Features("Themes")
@Stories("All Themes")
@RunWith(Parameterized.class)
public class ThemesTest {
    private static final Properties CONFIG = new Properties();

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() throws Exception {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Arrays.asList(RU, UA, BY, KZ)) {
            Themes themes = new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), d).themeActions().getCatalog().getThemes();
            for (ThemesEntry entry : getThemes(d)) {
                data.add(new Object[]{d, entry.getId(), themes});
            }
        }
        return data;
    }

    private String themeId;
    private Themes themes;

    public ThemesTest(Domain d, String themeId, Themes themes) {
        this.themeId = themeId;
        this.themes = themes;
    }

    @Test
    public void hasThemeInCleanvars() {
        assumeThat(themeId, not(anyOf(equalTo("bench"), equalTo("fifa2014"), equalTo("olymp2014"))));
//        String themeDescription = themes.getList().stream()
//                .filter(e -> e.getId().equals(themeId))
//                .findFirst()
//                .get()
//                .toString();
        assertThat(themes.getList().toString(), selectFirst(themes.getList(), having(on(Theme.class).getId(), equalTo(themeId))),
                notNullValue());
    }
}
