package ru.yandex.autotests.turkey.search;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.TuneSuggestPage;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.SearchSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.turkey.data.SearchData.SUGGEST_TESTS;
import static ru.yandex.autotests.turkey.data.SearchData.TUNE_SUGGEST_PAGE_URL;

/**
 * User: ivannik
 * Date: 15.05.2014
 */
@Aqua.Test(title = "Тесты саджеста")
@RunWith(Parameterized.class)
@Features("Search")
@Stories("Suggest")
public class SuggestTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private SearchSteps userSearch = new SearchSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);
    private TuneSuggestPage tuneSuggestPage = new TuneSuggestPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(SUGGEST_TESTS);
    }

    private String request;

    public SuggestTest(String request) {
        this.request = request;
    }


    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
    }

    @Test
    public void suggestAppears() {
        user.shouldSeeElement(yandexComTrPage.search.input);
        user.clearsInput(yandexComTrPage.search.input);
        user.entersTextInInput(yandexComTrPage.search.input, request);
        user.shouldSeeElement(yandexComTrPage.search.suggest);
        user.clicksOn(yandexComTrPage.search.input);
        user.clearsInput(yandexComTrPage.search.input);
        user.entersTextInInput(yandexComTrPage.search.input, "");
        user.shouldNotSeeElement(yandexComTrPage.search.suggest);
    }
}
