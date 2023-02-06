package ru.yandex.autotests.tunewebtests.retpath;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.aqua.annotations.project.Feature;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.tuneapitests.utils.Authorized;
import ru.yandex.autotests.tuneapitests.utils.Domain;
import ru.yandex.autotests.tuneapitests.utils.Language;
import ru.yandex.autotests.tuneclient.TuneClient;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserType;

import java.util.*;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.cookie.CookieManager.getSecretKey;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Проверка параметров retpath на тюне")
@Feature("Параметр retpath на Тюне")
@RunWith(Parameterized.class)
public class RetpathTest {

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);

    @Parameterized.Parameters(name = "Domain: \"{0}\"; {1}; Retpath: {2}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Domain d : Domain.values()) {
            for (Authorized auth : Authorized.values()) {
                data.add(new Object[]{d, auth, d.getYandexUrl(), equalTo(d.getYandexUrl())});
                data.add(new Object[]{d, auth,
                        d.getPogodaUrl().toString(),
                        matches("\\Q" + d.getPogodaUrl().toString() + "\\E/[\\w-]+(\\?ncrnd=\\d+)?")});
                data.add(new Object[]{d, auth, null, equalTo(d.getYandexUrl())});
            }
            data.add(new Object[]{d, Authorized.AUTH,
                    d.getMailUrl().toString() + "/#inbox",
                    matches("\\Q" + d.getMailUrl().toString() + "\\E/\\?(ncrnd=\\d+&)?uid=\\d+&login=[\\w-]+#inbox")});
        }
        return data;
    }

    private final Domain domain;
    private final Authorized authorized;
    private final String retpath;
    private final Matcher<String> targetUrl;
    private final User loginUser;

    public RetpathTest(Domain domain, Authorized authorized, String retpath, Matcher<String> targetUrl) {
        this.domain = domain;
        this.authorized = authorized;
        this.retpath = retpath;
        this.targetUrl = targetUrl;
        this.loginUser = mordaAllureBaseRule.getUser(UserType.DEFAULT);
    }

    @Before
    public void setUp() {
        user.opensPage(domain.getYandexUrl());
        if (Authorized.AUTH.equals(authorized)) {
            user.logsInAs(loginUser, domain.getBasePassportUrl(), domain.getYandexUrl());
        }
    }

    @Test
    public void languageRetpathTest() {
        String url = new TuneClient(domain.getTuneUrl())
                .language()
                .withIntl(Language.RU.getValue())
                .withSk(getSecretKey(driver))
                .withRetpath(retpath)
                .build().getUri().toString();
        user.opensPage(url, targetUrl);
    }

    @Test
    public void regionRetpathTest() {
        String url = new TuneClient(domain.getTuneUrlForGeoApi())
                .region()
                .withRegionId(RetpathData.REGION_FOR_DOMAIN.get(domain).getRegionId())
                .withSk(getSecretKey(driver))
                .withRetpath(retpath)
                .build().getUri().toString();
        user.opensPage(url, targetUrl);
    }

    @Test
    public void myRetpathTest() {
        String url = new TuneClient(domain.getTuneUrl())
                .my()
                .withBlock("8")
                .withParams(Collections.singletonList("120"))
                .withSk(getSecretKey(driver))
                .withRetpath(retpath)
                .build().getUri().toString();
        user.opensPage(url, targetUrl);
    }
}
