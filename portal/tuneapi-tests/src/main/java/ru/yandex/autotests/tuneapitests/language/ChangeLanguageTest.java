package ru.yandex.autotests.tuneapitests.language;


import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.tuneapitests.steps.ClientSteps;
import ru.yandex.autotests.tuneapitests.steps.LanguageSteps;
import ru.yandex.autotests.tuneapitests.utils.Authorized;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneapitests.utils.Language;
import ru.yandex.autotests.tuneclient.TuneClient;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.unauth;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Change Language")
@RunWith(Parameterized.class)
@Features("Language")
@Stories("Change Language")
public class ChangeLanguageTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Language: \"{1}\" -> \"{2}\"; {3} Retpath: {4}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Language lang1 : Language.values()) {
                for (Language lang2 : Language.values()) {
                    for (Authorized auth : Authorized.values()) {
                        data.add(new Object[]{d, lang1, lang2, auth, null});
                        data.add(new Object[]{d, lang1, lang2, auth, d.getYandexUrl()});
                    }
                }
            }
        }
        return data;
    }

    private final Client client;
    private final Domain domain;
    private final Language fromLang;
    private final Language toLang;
    private final Authorized authorized;
    private final String retpath;
    private final ClientSteps userClient;
    private final LanguageSteps userLanguage;

    public ChangeLanguageTest(Domain domain, Language fromLang, Language toLang, Authorized authorized,
                              String retpath) {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.fromLang = fromLang;
        this.toLang = toLang;
        this.authorized = authorized;
        this.retpath = retpath;
        this.userClient = new ClientSteps(client);
        this.userLanguage = new LanguageSteps(client, domain);
    }

    @Before
    public void setUp() {
        userClient.get(domain.getYandexUrl());
        userClient.authIfNeeded(authorized, domain);
        userLanguage.setLanguage(fromLang.getValue(), retpath);
        userLanguage.shouldSeeLanguage(fromLang);
    }

    @Test
    @Stories("Change Language")
    public void changeLanguage() throws IOException {
        userLanguage.setLanguage(toLang.getValue(), retpath);
        userLanguage.shouldSeeLanguage(toLang);
    }

    @Test
    @Stories("Change Language With Unauth sk in auth mode")
    public void languageChangedWithUnauthSk() {
        assumeThat(authorized, equalTo(Authorized.AUTH));
        userLanguage.setLanguageWithWrongSk(toLang.getValue(), unauth(domain, client), retpath);
        userLanguage.shouldSeeLanguage(toLang);
    }

}
