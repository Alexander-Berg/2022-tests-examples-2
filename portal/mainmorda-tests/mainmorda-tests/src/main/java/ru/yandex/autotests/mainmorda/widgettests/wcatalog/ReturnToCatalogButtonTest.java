package ru.yandex.autotests.mainmorda.widgettests.wcatalog;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.CatalogSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.WidgetsData.RANDOM_CUSTOM_WIDGET;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.RANDOM_CUSTOM_WIDGET_2;
import static ru.yandex.autotests.mainmorda.data.WidgetsData.getWidgetRubric;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Catalog.WIDGET_RETURN_CATALOG;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: alex89
 * Date: 10.01.13
 * //todo расширить тест проверкой кнопки "Добавить ещё виджеты", когда её починят.
 */

@Aqua.Test(title = "Кнопка возврата в каталог")
@Features({"Main", "Widget", "Widget Catalog"})
@Stories("Return Button")
public class ReturnToCatalogButtonTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private CatalogSteps userCatalog = new CatalogSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
    }

    /**
     * Добавляем виджет из каталога. Проверяем, что кнопка возврата ведет на правильную страницу каталога виджетов.
     */
    @Test
    public void catalogButtonIsPresentAndLeadsToCatalog() {
        userCatalog.addWidgetFromCatalog(getWidgetRubric(RANDOM_CUSTOM_WIDGET), RANDOM_CUSTOM_WIDGET);
        userWidget.acceptWidgetAddition();
        userCatalog.shouldSeeCatalogButtonInWidgetWithText(RANDOM_CUSTOM_WIDGET,
                getTranslation(WIDGET_RETURN_CATALOG, CONFIG.getLang()));
        userCatalog.shouldSeeThatCatalogButtonLeadsToCatalogPage();
    }

    /**
     * Добавляем виджет из каталога, проверяем наличие кнопки возврата, обновляем страницу -- кнопка должна исчезнуть.
     */
    @Test
    public void catalogButtonIsNotPresentAfterRefresh() {
        userCatalog.addWidgetFromCatalog(getWidgetRubric(RANDOM_CUSTOM_WIDGET), RANDOM_CUSTOM_WIDGET);
        userWidget.acceptWidgetAddition();
        userCatalog.shouldSeeCatalogButtonsOnPageInAmount(1);
        user.opensPage(CONFIG.getBaseURL());
        userCatalog.shouldSeeCatalogButtonsOnPageInAmount(0);
    }

    /**
     * Добавляем второй и третий виджеты; проверяем, что кнопка возврата правильно перемещается от одного
     * добавленного виджета к другому, ни в какой момент времени нет двух кнопок возврата на морде
     */
    @Test
    public void catalogButtonIsUniqueAfterSetOfWidgetAdditions() {
        userCatalog.addWidgetFromCatalog(getWidgetRubric(RANDOM_CUSTOM_WIDGET), RANDOM_CUSTOM_WIDGET);
        userWidget.acceptWidgetAddition();
        userCatalog.clicksOnCatalogButton();
        userCatalog.addWidgetFromCatalog(getWidgetRubric(RANDOM_CUSTOM_WIDGET_2), RANDOM_CUSTOM_WIDGET_2);
        userWidget.acceptWidgetAddition();
        userCatalog.shouldSeeCatalogButtonInWidgetWithText(RANDOM_CUSTOM_WIDGET_2,
                getTranslation(WIDGET_RETURN_CATALOG, CONFIG.getLang()));
        userCatalog.shouldSeeCatalogButtonsOnPageInAmount(1);
    }
}
