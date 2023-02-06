package ru.yandex.autotests.mordabackend.themes.v12;

import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.themes.Group;
import ru.yandex.autotests.mordabackend.beans.themes.Themes;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.Set;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */
public class ThemesGroupsV12Test {
    private static final Properties CONFIG = new Properties();

//    @Parameterized.Parameters(name = "{0}, {2}")
//    public static Collection<Object[]> data() throws Exception {
//        List<ThemesGroupV12Entry> groups = allExports(THEMES_GROUP_V12);
//        List<Object[]> data = new ArrayList<>();
//        for (Domain d : Arrays.asList(RU, UA, KZ, BY)) {
//            Themes themes = new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), d)
//                    .themeActions().getCatalog().getThemes();
//            List<String> themesForDomain = extract(getThemes(d), on(ThemesV12Entry.class).getId());
//            for (ThemesGroupV12Entry themesGroupV12Entry : groups) {
//                data.add(new Object[]{
//                                d,
//                                themes,
//                                themesGroupV12Entry.getId(),
//                                intersect(getGroupThemes(themesGroupV12Entry.getThemes()), themesForDomain)}
//                );
//            }
//        }
//        return data;
//    }

    private String groupId;
    private Themes themes;
    private Set<String> expectedThemes;

    public ThemesGroupsV12Test(Domain domain, Themes themes, String groupId, Set<String> expectedThemes) {
        this.groupId = groupId;
        this.expectedThemes = expectedThemes;
        this.themes = themes;
    }

//    @Test
    public void hasThemesInGroupV12() {
        System.out.println(expectedThemes);
        Group group = selectFirst(themes.getGroup(), having(on(Group.class).getId(), equalTo(groupId)));
        assertThat(group.toString(), group, notNullValue());
        assertThat(group.toString(), group.getThemesArray(), hasSameItemsAsCollection(expectedThemes));
        assertThat(group.toString(), expectedThemes, hasSameItemsAsCollection(group.getThemesArray()));
        assertThat(group.toString(), group.getThemesArray(), hasSize(expectedThemes.size()));
    }
}
