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

public class SetThemeTest {
    private static final Properties CONFIG = new Properties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(Arrays.asList(RU));
    }

    private final MordaClient mordaClient;
    private final Client client;
    private final String randomThemeId1;
    private final String randomThemeId2;

    public SetThemeTest(Domain domain) {
        this.mordaClient = new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), domain);
        this.client = getJsonEnabledClient();
        List<String> themes = extract(
                this.mordaClient.themeActions(getJsonEnabledClient()).getCatalog().getThemes().getList(),
                on(Theme.class).getId()
        );
        themes.removeAll(Arrays.asList(DEFAULT, RANDOM));
        Collections.shuffle(themes);
        randomThemeId1 = themes.get(0);
        randomThemeId2 = themes.get(1);
    }

//    @Test
    public void setSkin() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeTheme(newCleanvars, randomThemeId1);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), nullValue()));
    }

//    @Test
    public void setDefault() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), DEFAULT);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeDefaultTheme(newCleanvars);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), nullValue()));
    }

//    @Test
    public void setRandom() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeTheme(newCleanvars, RANDOM);
        shouldSeeRandomThemeParameters(mordaClient, client, newCleanvars);
    }

//    @Test
    public void setThemeAfterTheme() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();

        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId2);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeTheme(newCleanvars, randomThemeId2);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), nullValue()));
    }

//    @Test
    public void setDefaultAfterTheme() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();

        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);
        setTheme(mordaClient, client, cleanvars.getSk(), DEFAULT);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeDefaultTheme(newCleanvars);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), nullValue()));
    }

//    @Test
    public void setRandomAfterTheme() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();

        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeTheme(newCleanvars, RANDOM);
        shouldSeeRandomThemeParameters(mordaClient, client, newCleanvars);
    }

//    @Test
    public void setThemeAfterDefault() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();

        setTheme(mordaClient, client, cleanvars.getSk(), DEFAULT);
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeTheme(newCleanvars, randomThemeId1);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), nullValue()));
    }

//    @Test
    public void setRandomAfterDefault() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();

        setTheme(mordaClient, client, cleanvars.getSk(), DEFAULT);
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeTheme(newCleanvars, RANDOM);
        shouldSeeRandomThemeParameters(mordaClient, client, newCleanvars);
    }

//    @Test
    public void setDefaultAfterRandom() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);
        setTheme(mordaClient, client, cleanvars.getSk(), DEFAULT);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeDefaultTheme(newCleanvars);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), notNullValue()));
    }

//    @Test
    public void setThemeAfterRandom() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeTheme(newCleanvars, randomThemeId1);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), notNullValue()));
    }

}
