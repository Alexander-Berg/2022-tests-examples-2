package ru.yandex.autotests.mordabackend.themes;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.themes.Themes;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_COMTR;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_GROUP_COMTR;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.allExports;
import static ru.yandex.autotests.utils.morda.url.Domain.*;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */
public class ThemesCountTest {
    private static final Properties CONFIG = new Properties();
    private static final Cleanvars CLEANVARS_RU =
            new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), RU).themeActions().getCatalog();
    private static final Cleanvars CLEANVARS_UA =
            new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), UA).themeActions().getCatalog();
    private static final Cleanvars CLEANVARS_BY =
            new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), BY).themeActions().getCatalog();
    private static final Cleanvars CLEANVARS_KZ =
            new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), KZ).themeActions().getCatalog();
    private static final Cleanvars CLEANVARS_COM_TR =
            new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), COM_TR).themeActions().getCatalog();

//    @Test
//    public void themesNumberRu() {
//        shouldHaveParameter(CLEANVARS_RU.getThemes(), having(on(Themes.class).getList(),
//                hasSize(getThemes(RU).size())));
//    }
//
//    @Test
//    public void themesNumberUa() {
//        shouldHaveParameter(CLEANVARS_UA.getThemes(), having(on(Themes.class).getList(),
//                hasSize(getThemes(UA).size())));
//    }
//
//    @Test
//    public void themesNumberBy() {
//        shouldHaveParameter(CLEANVARS_BY.getThemes(), having(on(Themes.class).getList(),
//                hasSize(getThemes(BY).size())));
//    }
//
//    @Test
//    public void themesNumberKz() {
//        shouldHaveParameter(CLEANVARS_KZ.getThemes(), having(on(Themes.class).getList(),
//                hasSize(getThemes(KZ).size())));
//    }
//
//    @Test
//    public void groupsNumberKubr() {
//        shouldHaveParameter(CLEANVARS_RU.getThemes(), having(on(Themes.class).getGroup(),
//                hasSize(allExports(THEMES_GROUP_V12).size())));
//    }

//    @Test
    public void themesNumberComTr() {
        shouldHaveParameter(CLEANVARS_COM_TR.getThemes(), having(on(Themes.class).getList(),
                hasSize(allExports(THEMES_COMTR).size())));
    }

//    @Test
    public void groupsNumberComTr() {
        shouldHaveParameter(CLEANVARS_COM_TR.getThemes(), having(on(Themes.class).getGroup(),
                hasSize(allExports(THEMES_GROUP_COMTR).size())));
    }
}
