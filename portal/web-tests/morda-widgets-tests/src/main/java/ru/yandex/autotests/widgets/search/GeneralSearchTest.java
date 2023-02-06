package ru.yandex.autotests.widgets.search;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.Properties;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.autotests.widgets.steps.WidgetSteps;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.widgets.data.SearchData.REQUESTS;

/**
 * User: leonsabr
 * Date: 08.11.11
 * Поиск по каталогу виджетов: слова и словосочетания, бренды.
 */
@Aqua.Test(title = "Поиск через форму")
@Features("Search")
@RunWith(Parameterized.class)
public class GeneralSearchTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return convert(REQUESTS);
    }

    private String request;
    private List<String> responses;

    public GeneralSearchTest(String request, List<String> responses) {
        this.request = request;
        this.responses = responses;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }


    @Test
    public void search() {
        user.shouldSeeElement(widgetPage.searchField);
        user.entersTextInInput(widgetPage.searchField, request);
        user.shouldSeeElement(widgetPage.searchButton);
        user.clicksOn(widgetPage.searchButton);
        userWidget.shouldSeeWidgetWithTextIn(widgetPage.allWidgets, responses);
    }
}
