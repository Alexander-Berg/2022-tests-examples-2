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

import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.empty;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.nullSk;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.random;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.withoutFirstLetter;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Change Language With Bad Sk")
@RunWith(Parameterized.class)
@Features("Language")
public class ChangeLanguageWithBadSkTest {

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

    public ChangeLanguageWithBadSkTest(Domain domain, Language fromLang, Language toLang, Authorized authorized, String retpath) {
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
    @Stories("Change Language With No sk")
    public void languageNotChangedWithoutSk() throws IOException {
        userLanguage.setLanguageWithWrongSk(toLang.getValue(), nullSk(), retpath);
        userLanguage.shouldSeeLanguage(fromLang);
    }

    @Test
    @Stories("Change Language With Empty sk")
    public void languageNotChangedWithEmptySk() throws IOException {
        userLanguage.setLanguageWithWrongSk(toLang.getValue(), empty(), retpath);
        userLanguage.shouldSeeLanguage(fromLang);
    }

    @Test
    @Stories("Change Language With Sk without first letter")
    public void languageNotChangedWithoutFirstLetterOfSk() {
        userLanguage.setLanguageWithWrongSk(toLang.getValue(), withoutFirstLetter(domain, client), retpath);
        userLanguage.shouldSeeLanguage(fromLang);
    }

    @Test
    @Stories("Change Language With Random sk")
    public void languageNotChangedWithRandomSk() {
        userLanguage.setLanguageWithWrongSk(toLang.getValue(), random(domain, client), retpath);
        userLanguage.shouldSeeLanguage(fromLang);
    }

}
