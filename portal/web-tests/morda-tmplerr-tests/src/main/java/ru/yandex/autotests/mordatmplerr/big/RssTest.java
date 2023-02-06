package ru.yandex.autotests.mordatmplerr.big;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.data.WidgetsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.CatalogSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.autotests.mordatmplerr.mordatypes.Browser;
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19.03.14
 */

@Aqua.Test(title = "RSS Widget")
@Features({"Big", "RSS Wirdget"})
@RunWith(Parameterized.class)
public class RssTest {
    private static final Properties CONFIG = new Properties();
    private final String urlBig;
    private final String urlEdit;

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private WidgetSteps userWidget;
    private CatalogSteps userCatalog;
    private MainPage mainPage;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        for (Browser browser : Browser.values()) {
            data.add(mainMorda(RU).withBrowser(browser));
        }
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public RssTest(Morda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.mainPage = new MainPage(driver);
        this.userWidget = new WidgetSteps(driver);
        this.userCatalog = new CatalogSteps(driver);
        urlBig = morda.getUrl(CONFIG.getMordaEnv().getEnv());
        urlEdit = urlBig + "?edit=1";
    }

    @Test
    public void addRssWidget() {
        user.opensPage(urlBig);
        userWidget.addWidget(urlBig, WidgetsData.LENTARU.getName());
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void addRssWidgetInEditMode() {
        user.opensPage(urlEdit);
        userWidget.addWidgetInEditMode(WidgetsData.LENTARU.getName());
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void editRssWidget() {
        user.opensPage(urlEdit);
        userWidget.addWidgetInEditMode(WidgetsData.LENTARU.getName());
        user.shouldSeeElement(mainPage.rssWidget);
        user.shouldSeeElement(mainPage.rssWidget.editIcon);
        user.clicksOn(mainPage.rssWidget.editIcon);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void addRssWidgetFromCatalogAccept() {
        user.opensPage(urlBig);
        userCatalog.addWidgetFromCatalog(WidgetsData.getWidgetRubric(WidgetsData.LENTARU), WidgetsData.LENTARU);
        userCatalog.acceptWidgetAddition();
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }

    @Test
    public void addRssWidgetFromCatalogDecline() {
        user.opensPage(urlBig);
        userCatalog.addWidgetFromCatalog(WidgetsData.getWidgetRubric(WidgetsData.LENTARU), WidgetsData.LENTARU);
        userCatalog.declineWidgetAddition();
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
    }
}
