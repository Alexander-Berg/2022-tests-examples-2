package ru.yandex.autotests.mainmorda.commontests.searchform;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mainmorda.data.SearchData.REDIRECT_EXPECTED_URL_MATCHER;
import static ru.yandex.autotests.mainmorda.data.SearchData.REDIRECT_URL_PATTERN;
import static ru.yandex.autotests.mainmorda.data.SearchData.SearchType;
import static ru.yandex.autotests.mainmorda.data.SearchData.SearchType.getExpectedUrl;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.13
 */
@Aqua.Test(title = "Редирект на серп при запросе")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Search Form"})
@Stories("Redirect")
public class RedirectTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
    }

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<Object[]>();
        for (Domain d : Domain.values()) {
            for (SearchType type : SearchType.values()) {
                data.add(new Object[]{d, type});
            }
        }
        return data;
    }

    private Domain domain;
    private SearchType type;

    public RedirectTest(Domain domain, SearchType type) {
        this.domain = domain;
        this.type = type;
    }

    @Test
    public void redirect() {
        user.opensPage(String.format(REDIRECT_URL_PATTERN, domain, type.getSearch()), getExpectedUrl(type, domain));
        user.shouldSeePage(REDIRECT_EXPECTED_URL_MATCHER);
    }

}

