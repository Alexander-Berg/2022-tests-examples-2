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

import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.empty;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.nullSk;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.random;
import static ru.yandex.autotests.tuneapitests.utils.BadSkProvider.withoutFirstLetter;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Set Language With Bad Sk")
@RunWith(Parameterized.class)
@Features("Language")
public class SetLanguageWithBadSkTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Language: \"{1}\"; {2}; Retpath: {3}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Language lang : Language.values()) {
                for (Authorized auth : Authorized.values()) {
                    data.add(new Object[]{d, lang, auth, null});
                    data.add(new Object[]{d, lang, auth, d.getYandexUrl()});
                }
            }
        }
        return data;
    }

    private final Client client;
    private final Domain domain;
    private final Language language;
    private final String retpath;
    private final Authorized authorized;
    private final ClientSteps userClient;
    private final LanguageSteps userLanguage;

    public SetLanguageWithBadSkTest(Domain domain, Language language, Authorized authorized, String retpath) {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.language = language;
        this.authorized = authorized;
        this.retpath = retpath;
        this.userClient = new ClientSteps(client);
        this.userLanguage = new LanguageSteps(client, domain);
    }

    @Before
    public void setUp() {
        userClient.get(domain.getYandexUrl());
        userClient.authIfNeeded(authorized, domain);
    }

    @Test
    @Stories("Set Language With No sk")
    public void languageNotSetWithoutSk() {
        userLanguage.setLanguageWithWrongSk(language.getValue(), nullSk(), retpath);
        userLanguage.shouldNotSeeLanguageSet();
    }

    @Test
    @Stories("Set Language With Empty sk")
    public void languageNotSetWithEmptySk() {
        userLanguage.setLanguageWithWrongSk(language.getValue(), empty(), retpath);
        userLanguage.shouldNotSeeLanguageSet();
    }

    @Test
    @Stories("Set Language With Sk without first letter")
    public void languageNotSetWithoutFirstLetterOfSk() {
        userLanguage.setLanguageWithWrongSk(language.getValue(), withoutFirstLetter(domain, client), retpath);
        userLanguage.shouldNotSeeLanguageSet();
    }

    @Test
    @Stories("Set Language With Random sk")
    public void languageNotSetWithRandomSk() {
        userLanguage.setLanguageWithWrongSk(language.getValue(), random(domain, client), retpath);
        userLanguage.shouldNotSeeLanguageSet();
    }
}
