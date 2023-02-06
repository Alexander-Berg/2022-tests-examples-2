package ru.yandex.autotests.mainmorda.commontests.news;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.NewsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.NewsBlockData.DIVIDER_MATCHER;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.HOUR_MATCHER;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.MINUTE_MATCHER;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.TIME_HREF;

/**
 * User: alex89
 * Date: 17.04.12
 * Проверка ДАТЫ и ВРЕМЕНИ в блоке новостей
 */
@Aqua.Test(title = "Дата и время")
@Features({"Main", "Common", "News Block"})
@Stories("Time")
public class NewsTimeTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private NewsSteps userNews = new NewsSteps(driver);
    private LinksSteps userLinks = new LinksSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.newsBlock);
    }

    @Test
    public void dateAndTimeText() {
        user.shouldSeeElement(mainPage.newsBlock.time);
        user.shouldSeeElement(mainPage.newsBlock.date);
        user.shouldSeeElementWithText(mainPage.newsBlock.time.hours, HOUR_MATCHER);
        user.shouldSeeElementWithText(mainPage.newsBlock.time.minutes, MINUTE_MATCHER);
        user.shouldSeeElementWithText(mainPage.newsBlock.time.divider, DIVIDER_MATCHER);
        userNews.shouldSeeActualTime();
        userNews.shouldSeeActualDate();
    }

    @Test
    public void dateAndTimeDoesNotDisappears() {
        userNews.switchToTab(mainPage.newsBlock.regNewsTab);
        user.shouldSeeElement(mainPage.newsBlock.time);
        user.shouldSeeElement(mainPage.newsBlock.date);
        userNews.switchToTab(mainPage.newsBlock.mainNewsTab);
        user.shouldSeeElement(mainPage.newsBlock.time);
        user.shouldSeeElement(mainPage.newsBlock.date);
    }

    @Test
    public void timeLink() {
        user.shouldSeeElement(mainPage.newsBlock.time);
        userLinks.shouldSeeHref(mainPage.newsBlock.time, TIME_HREF);
    }

}
