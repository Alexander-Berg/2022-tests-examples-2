package ru.yandex.autotests.mordabackend.themes;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.themes.Theme;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesEntry;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */
public class ThemesUtils {
    private static final Properties CONFIG = new Properties();
    public static final String DEFAULT = "default";
    public static final String RANDOM = "random";
    public static final String GALATASARAY = "galatasaray";
    public static final String FENERBAHCE = "fenerbahce";
    public static final String BESIKTAS = "besiktas";

    public static final Map<String, String> FOOTBALL_PAGES = new HashMap<String, String>() {{
        put(GALATASARAY, "gs");
        put(FENERBAHCE, "fb");
        put(BESIKTAS, "bjk");
    }};

    public static List<String> getGroupThemes(String themes) {
        String[] themesRaw = themes.split(",");
        List<String> groupThemes = new ArrayList<>();
        for (String theme : themesRaw) {
            if (theme.trim().length() > 0) {
                groupThemes.add(theme.trim());
            }
        }
        return groupThemes;
    }

    @Step("Set skin {3}")
    public static void setTheme(MordaClient mordaClient, Client client, String sk, String themeId) {
        mordaClient.themeActions(client).set(themeId, sk);
    }

    @Step("Choose skin {1} in catalog")
    public static Cleanvars chooseTheme(MordaClient mordaClient, Client client, String themeId) {
        return mordaClient.themeActions(client).choose(themeId);
    }

    @Step("Open football page {1}")
    public static Cleanvars openFootball(MordaClient mordaClient, Client client, String themeId) {
        return mordaClient.themeActions(client).setFootball(FOOTBALL_PAGES.get(themeId));
    }

    @Step("Open catalog")
    public static Cleanvars getCatalog(MordaClient mordaClient, Client client) {
        return mordaClient.themeActions(client).getCatalog();
    }

    @Step("Should see default skin")
    public static void shouldSeeDefaultTheme(Cleanvars cleanvars) {
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getSkin(), nullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings(), notNullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings().getDefskin(), nullValue()));
    }

    @Step("Should see random skin parameters")
    public static void shouldSeeRandomThemeParameters(MordaClient mordaClient, Client client, Cleanvars cleanvars) {
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getRandomSkin(), notNullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings(), notNullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), notNullValue()));

        List<String> themes = extract(mordaClient.themeActions(client).getCatalog().getThemes().getList(),
                on(Theme.class).getId());
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getRandomSkin(), isIn(themes)));
    }

    @Step("Should see skin {1}")
    public static void shouldSeeTheme(Cleanvars cleanvars, String themeId) {
        System.out.println(cleanvars.getSkin());
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getSkin(), equalTo(themeId)));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings(), notNullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings().getDefskin(), equalTo(themeId)));
    }

    @Step("Should see football parameters")
    public static void shouldSeeFootballParameters(Cleanvars cleanvars) {
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getFootballTr(), notNullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getFootballTr().getExp(), equalTo("skin")));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getFootballTr().getProcessed(), equalTo(1)));
    }

    @Step("Should see skins catalog")
    public static void shouldSeeThemesCatalog(Cleanvars cleanvars) {
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getSkinsCatalog(), equalTo(1)));
    }

    @Step("Should see chosen skin {1} in catalog")
    public static void shouldSeeChosenThemeInCatalog(Cleanvars cleanvars, String themeId) {
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getDefskinArg(), equalTo(themeId)));
    }

    public static List<ThemesEntry> getThemes(Domain domain) {
        if (!domain.equals(UA)) {
            return exports(THEMES, anyOf(domain(isEmptyOrNullString()), domain(domain), domain("kubr-ua")),
                    having(on(ThemesEntry.class).getPreview(), isEmptyOrNullString()));
//                    having(on(ThemesEntry.class).getHidden(), equalTo(0)));
        } else {
            return exports(THEMES, domain(UA));
//                    having(on(ThemesEntry.class).getHidden(), equalTo(0)));
        }
    }
}
