package ru.yandex.autotests.mordabackend.themes.comtr;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.themes.Group;
import ru.yandex.autotests.mordabackend.beans.themes.Themes;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesGroupComtrEntry;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordabackend.themes.ThemesUtils.getGroupThemes;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_GROUP_COMTR;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.allExports;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */

public class ThemesGroupsComTrTest {
    private static final Properties CONFIG = new Properties();
    private static final Themes THEMES = new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), COM_TR)
            .themeActions().getCatalog().getThemes();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() throws Exception {
        List<ThemesGroupComtrEntry> groups = allExports(THEMES_GROUP_COMTR);
        List<Object[]> data = new ArrayList<>();
        for (ThemesGroupComtrEntry themesGroupComtrEntry : groups) {
            data.add(new Object[]{themesGroupComtrEntry.getId(), getGroupThemes(themesGroupComtrEntry.getThemes())});
        }
        return data;
    }

    private String groupId;
    private List<String> expectedThemes;

    public ThemesGroupsComTrTest(String groupId, List<String> expectedThemes) {
        this.groupId = groupId;
        this.expectedThemes = expectedThemes;
    }

//    @Test
    public void hasThemesInGroupComTr() {
        Group group = selectFirst(THEMES.getGroup(), having(on(Group.class).getId(), equalTo(groupId)));
        assertThat(group.toString(), group, notNullValue());
        assertThat(group.toString(), group.getThemesArray(), hasItems(expectedThemes.toArray(new String[0])));
        assertThat(group.toString(), expectedThemes, hasItems(group.getThemesArray().toArray(new String[0])));
        assertThat(group.toString(), group.getThemesArray(), hasSize(expectedThemes.size()));
    }
}
