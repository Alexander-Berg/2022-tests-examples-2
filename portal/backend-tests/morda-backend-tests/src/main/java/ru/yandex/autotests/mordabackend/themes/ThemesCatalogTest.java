package ru.yandex.autotests.mordabackend.themes;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.themes.Theme;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.url.Domain;

import javax.ws.rs.client.Client;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.mordabackend.MordaClient.getJsonEnabledClient;
import static ru.yandex.autotests.mordabackend.themes.ThemesUtils.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */

public class ThemesCatalogTest {
    private static final Properties CONFIG = new Properties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(Arrays.asList(RU));
    }

    private final MordaClient mordaClient;
    private final Client client;
    private final String randomThemeId1;
    private final String randomThemeId2;

    public ThemesCatalogTest(Domain domain) {
        this.mordaClient = new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), domain);
        this.client = getJsonEnabledClient();
        List<String> themes = extract(mordaClient.themeActions().getCatalog().getThemes().getList(),
                on(Theme.class).getId());
        themes.removeAll(Arrays.asList(DEFAULT, RANDOM));
        Collections.shuffle(themes);
        randomThemeId1 = themes.get(0);
        randomThemeId2 = themes.get(1);
    }

//    @Test
    public void openCatalog() {
        Cleanvars cleanvars = getCatalog(mordaClient, client);
        shouldSeeThemesCatalog(cleanvars);
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings(), nullValue()));
    }

//    @Test
    public void openCatalogAndChooseTheme() {
        Cleanvars cleanvars = chooseTheme(mordaClient, client, randomThemeId1);
        shouldSeeThemesCatalog(cleanvars);
        shouldSeeChosenThemeInCatalog(cleanvars, randomThemeId1);
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings(), nullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

//    @Test
    public void openCatalogAndChooseRandom() {
        Cleanvars cleanvars = chooseTheme(mordaClient, client, RANDOM);
        shouldSeeThemesCatalog(cleanvars);
        shouldSeeChosenThemeInCatalog(cleanvars, RANDOM);
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings(), nullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getRandomSkin(), notNullValue()));
    }

//    @Test
    public void openCatalogAndChooseDefault() {
        Cleanvars cleanvars = chooseTheme(mordaClient, client, DEFAULT);
        shouldSeeThemesCatalog(cleanvars);
        shouldSeeChosenThemeInCatalog(cleanvars, DEFAULT);
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getWPSettings(), nullValue()));
        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

//    @Test
    public void setThemeAndOpenCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);

        Cleanvars newCleanvars = getCatalog(mordaClient, client);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeTheme(newCleanvars, randomThemeId1);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

//    @Test
    public void setRandomAndOpenCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);

        Cleanvars newCleanvars = getCatalog(mordaClient, client);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeTheme(newCleanvars, RANDOM);
        shouldSeeRandomThemeParameters(mordaClient, client, newCleanvars);
    }

//    @Test
    public void setDefaultAndOpenCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), DEFAULT);

        Cleanvars newCleanvars = getCatalog(mordaClient, client);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeDefaultTheme(newCleanvars);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

//    @Test
    public void setThemeAndChooseNewThemeInCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);

        Cleanvars newCleanvars = chooseTheme(mordaClient, client, randomThemeId2);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeChosenThemeInCatalog(newCleanvars, randomThemeId2);
        shouldSeeTheme(newCleanvars, randomThemeId1);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

//    @Test
    public void setThemeAndChooseDefaultInCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);

        Cleanvars newCleanvars = chooseTheme(mordaClient, client, DEFAULT);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeChosenThemeInCatalog(newCleanvars, DEFAULT);
        shouldSeeTheme(newCleanvars, randomThemeId1);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

//    @Test
    public void setThemeAndChooseRandomInCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);

        Cleanvars newCleanvars = chooseTheme(mordaClient, client, RANDOM);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeChosenThemeInCatalog(newCleanvars, RANDOM);
        shouldSeeTheme(newCleanvars, randomThemeId1);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), notNullValue()));
    }

//    @Test
    public void setDefaultAndChooseNewThemeInCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), DEFAULT);

        Cleanvars newCleanvars = chooseTheme(mordaClient, client, randomThemeId2);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeChosenThemeInCatalog(newCleanvars, randomThemeId2);
        shouldSeeDefaultTheme(newCleanvars);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

//    @Test
    public void setDefaultAndChooseRandomInCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), DEFAULT);

        Cleanvars newCleanvars = chooseTheme(mordaClient, client, RANDOM);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeChosenThemeInCatalog(newCleanvars, RANDOM);
        shouldSeeDefaultTheme(newCleanvars);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), notNullValue()));
    }

//    @Test
    public void setRandomAndChooseNewThemeInCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);

        Cleanvars newCleanvars = chooseTheme(mordaClient, client, randomThemeId2);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeChosenThemeInCatalog(newCleanvars, randomThemeId2);
        shouldSeeTheme(newCleanvars, RANDOM);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

//    @Test
    public void setRandomAndChooseDefaultInCatalog() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);

        Cleanvars newCleanvars = chooseTheme(mordaClient, client, DEFAULT);
        shouldSeeThemesCatalog(newCleanvars);
        shouldSeeChosenThemeInCatalog(newCleanvars, DEFAULT);
        shouldSeeTheme(newCleanvars, RANDOM);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getRandomSkin(), nullValue()));
    }

}
