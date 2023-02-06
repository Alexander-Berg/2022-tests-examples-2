package ru.yandex.autotests.mordabackend.themes.v12;

import ru.yandex.autotests.mordabackend.Properties;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */

public class ThemesListV12Test {
    private static final Properties CONFIG = new Properties();

//    @Parameterized.Parameters(name = "{0}, {1}")
//    public static Collection<Object[]> data() throws Exception {
//        List<Object[]> data = new ArrayList<>();
//        for (Domain d : Arrays.asList(RU, UA, KZ, BY)) {
//            Themes themes = new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), d).themeActions().getCatalog().getThemes();
//            for (ThemesV12Entry entry : getThemes(d)) {
//                data.add(new Object[] {d, entry.getId(), themes});
//            }
//        }
//        return data;
//    }
//
//    private String themeId;
//    private Themes themes;
//
//    public ThemesListV12Test(Domain d, String themeId, Themes themes) {
//        this.themeId = themeId;
//        this.themes = themes;
//    }
//
//    @Test
//    public void hasThemeInCleanvarsV12() {
//        assertThat(themes.toString(), selectFirst(themes.getList(), having(on(Theme.class).getId(), equalTo(themeId))),
//                notNullValue());
//    }
}
