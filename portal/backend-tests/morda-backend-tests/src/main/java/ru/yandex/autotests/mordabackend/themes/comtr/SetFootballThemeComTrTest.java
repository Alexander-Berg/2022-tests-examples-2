package ru.yandex.autotests.mordabackend.themes.comtr;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.themes.Theme;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;

import javax.ws.rs.client.Client;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static ch.lambdaj.Lambda.*;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.mordabackend.MordaClient.getJsonEnabledClient;
import static ru.yandex.autotests.mordabackend.themes.ThemesUtils.*;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 13.05.14
 */

public class SetFootballThemeComTrTest {
    private static final Properties CONFIG = new Properties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(Arrays.asList(FENERBAHCE, GALATASARAY, BESIKTAS));
    }

    private final MordaClient mordaClient;
    private final Client client;
    private final String footballThemeId;
    private final String randomThemeId1;

    public SetFootballThemeComTrTest(String footballThemeId) {
        this.mordaClient = new MordaClient(CONFIG.getProtocol(), CONFIG.getMordaEnv(), COM_TR);
        this.client = getJsonEnabledClient();
        this.footballThemeId = footballThemeId;
        List<String> themes = extract(mordaClient.themeActions().getCatalog().getThemes().getList(),
                on(Theme.class).getId());
        themes.removeAll(Arrays.asList(DEFAULT, RANDOM));
        Collections.shuffle(themes);
        randomThemeId1 = themes.get(0);
    }

//    @Test
    public void setFootball() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), footballThemeId);

        Cleanvars newCleanvars = mordaClient.cleanvarsActions(client).get();

        shouldSeeTheme(newCleanvars, footballThemeId);
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), nullValue()));
    }

//    @Test
    public void openFootballPage() {
        Cleanvars cleanvars = openFootball(mordaClient, client, footballThemeId);

        shouldHaveParameter(cleanvars, having(on(Cleanvars.class).getSkin(), equalTo(footballThemeId)));
    }

//    @Test
    public void setThemeAndOpenFootballPage() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), randomThemeId1);

        Cleanvars newCleanvars = openFootball(mordaClient, client, footballThemeId);

        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getSkin(), equalTo(footballThemeId)));
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings(), notNullValue()));
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getDefskin(),
                equalTo(randomThemeId1)));
    }

//    @Test
    public void setRandomAndOpenFootballPage() {
        Cleanvars cleanvars = mordaClient.cleanvarsActions(client).get();
        setTheme(mordaClient, client, cleanvars.getSk(), RANDOM);

        Cleanvars newCleanvars = openFootball(mordaClient, client, footballThemeId);

        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getSkin(), equalTo(footballThemeId)));
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings(), notNullValue()));
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getDefskin(), equalTo(RANDOM)));
        shouldHaveParameter(newCleanvars, having(on(Cleanvars.class).getWPSettings().getRandomSkin(), notNullValue()));
    }
}