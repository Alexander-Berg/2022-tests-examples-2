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
import ru.yandex.autotests.tuneclient.TuneResponse;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.junit.Assume.assumeTrue;

/**
 * User: leonsabr
 * Date: 08.06.12
 */
@Aqua.Test(title = "Set Language Json")
@RunWith(Parameterized.class)
@Features("Language")
@Stories("Set Language Json")
public class SetLanguageJsonTest {

    @Parameterized.Parameters(name = "Domain: \"{0}\"; Language: \"{1}\"; {2}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Language lang : Language.values()) {
                for (Authorized auth : Authorized.values()) {
                    data.add(new Object[]{d, lang, auth});
                }
            }
        }
        return data;
    }

    private final Client client;
    private final Domain domain;
    private final Language language;
    private final Authorized authorized;
    private final ClientSteps userClient;
    private final LanguageSteps userLanguage;

    public SetLanguageJsonTest(Domain domain, Language language, Authorized authorized) {
        this.client = TuneClient.getClient();
        this.domain = domain;
        this.language = language;
        this.authorized = authorized;
        this.userClient = new ClientSteps(client);
        this.userLanguage = new LanguageSteps(client, domain);
    }

    @Before
    public void setUp() {
        userClient.get(domain.getYandexUrl());
        userClient.authIfNeeded(authorized, domain);
    }

    @Test
    @Stories("Set Language Json")
    public void setLanguageJson() {
        assumeTrue("Domain is invalid", domain.isDomainValidForJsonRequest());
        TuneResponse response = userLanguage.setLanguageJson(language.getValue(), "1");
        userClient.shouldSeeOkTuneResponse(response);
        userLanguage.shouldSeeLanguage(language);
    }

    @Test
    @Stories("Error Language Json With Invalid Domain")
    public void errorLanguageJsonInvalidDomain() {
        assumeTrue("Domain is valid", !domain.isDomainValidForJsonRequest());
        TuneResponse response = userLanguage.setLanguageJson(language.getValue(), "1");
        userClient.shouldSeeErrorTuneResponse(response);
        userLanguage.shouldNotSeeLanguageSet();
    }

    @Test
    @Stories("Error Language Json With No sk")
    public void errorLanguageJsonWithoutSk() {
        TuneResponse response = userLanguage.setLanguageJsonWithoutSk(language.getValue(), "1");
        userClient.shouldSeeErrorTuneResponse(response);
        userLanguage.shouldNotSeeLanguageSet();
    }

    @Test
    @Stories("Set Language Json On Tune Internal")
    public void setLanguageOnTuneInternal() {
        TuneResponse response = userLanguage.setLanguageJsonOnTuneInternal(language.getValue(), null);
        userClient.shouldSeeOkTuneResponse(response);
        userLanguage.shouldSeeLanguage(language);
    }

}
