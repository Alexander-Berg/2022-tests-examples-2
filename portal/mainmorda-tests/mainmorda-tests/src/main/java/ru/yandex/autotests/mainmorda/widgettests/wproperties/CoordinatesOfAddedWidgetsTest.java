package ru.yandex.autotests.mainmorda.widgettests.wproperties;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PatternsSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mainmorda.utils.WidgetPattern;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.RANDOM_CUSTOM_WIDGET;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 31.01.13
 */

@Aqua.Test(title = "Координаты виджетов при сохранении паттерна (при добавлении виджетов)")
@Features({"Main", "Widget", "Widget Properties"})
@Stories("Coordinates")
public class CoordinatesOfAddedWidgetsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private PatternsSteps userPattern = new PatternsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
    }

    /**
     * Режим редактирования: Добавляем электрички, затем новый виджет (случайно выбранный из Фотки,Лента, Метро, РБК)
     * и
     * проверяем координатный запрос.
     * Пример координатной части запроса (добавлена Лента.Ру):
     * (&widget=_topnewsblogs-1&coord=1%3A1&usrCh=0&widget=_teaser-1&coord=2%3A1&usrCh=0
     * &widget=_geo-1&coord=3%3A1&usrCh=0&widget=_weather-1&coord=4%3A1&usrCh=0&widget=_traffic-1&coord=5%3A1&usrCh=0
     * &widget=_services-1&coord=3%3A2&usrCh=0&widget=_tvafisha-1&coord=4%3A2&usrCh=0
     * &widget=_stocks-1&coord=5%3A2&usrCh=0&widget=_etrains-2&coord=3%3A4&usrCh=1
     * &widget=_etrains-1&coord=3%3A5&usrCh=0&widget=_etrains-3&coord=3%3A3&usrCh=3&widget=28-2&coord=4%3A3&usrCh=1)
     */

    @Test
    public void coordinatesAreCorrectInCaseOfWidgetAddition() {
        WidgetPattern workPattern = userPattern.getPatternInEditMode();

        userWidget.editTvWidget(workPattern);
        userWidget.saveSettings(workPattern);
        userWidget.addWidgetInEditMode(RANDOM_CUSTOM_WIDGET.getName(), workPattern);

        userPattern.shouldSeePatternRequest(workPattern);
    }
}
