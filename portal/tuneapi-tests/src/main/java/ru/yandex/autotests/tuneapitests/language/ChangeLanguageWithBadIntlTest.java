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
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Change Language With Bad Intl")
@RunWith(Parameterized.class)
@Features("Language")
@Stories("Change Language With Bad Intl")
public class ChangeLanguageWithBadIntlTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Language: \"{1}\" -> \"{2}\"; {3} Retpath: {4}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Language lang1 : Language.values()) {
                for (String lang2 : LanguageData.BAD_INTLS) {
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
    private final String toLang;
    private final Authorized authorized;
    private final String retpath;
    private final ClientSteps userClient;
    private final LanguageSteps userLanguage;

    public ChangeLanguageWithBadIntlTest(Domain domain, Language fromLang, String toLang, Authorized authorized,
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
    public void languageNotChangedWithBadIntl() {
        userLanguage.setLanguage(toLang, retpath);
        userLanguage.shouldSeeLanguage(fromLang);
    }

}
