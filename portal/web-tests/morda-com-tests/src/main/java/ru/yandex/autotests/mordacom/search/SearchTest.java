package ru.yandex.autotests.mordacom.search;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.SerpComPage;
import ru.yandex.autotests.mordacom.steps.SearchSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacom.data.SearchData.SEARCH_TEST_DATA;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
@Aqua.Test(title = "Проброс запроса в поиск")
@RunWith(Parameterized.class)
@Features("Search")
@Stories("Request")
public class SearchTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private SearchSteps userSearch = new SearchSteps(driver);
    private SerpComPage serpComPage = new SerpComPage(driver);

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Language language : CONFIG.getMordaComLangs()) {
            for (String request : SEARCH_TEST_DATA) {
                data.add(new Object[]{language, request});
            }
        }
        return data;
    }

    private final Language language;
    private final String request;

    public SearchTest(Language language, String request) {
        this.language = language;
        this.request = request;
    }

    @Test
    public void requestIsThrownInSerp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        userSearch.searchFor(request);
        user.shouldSeeInputWithText(serpComPage.arrow.input, request);
    }
}
