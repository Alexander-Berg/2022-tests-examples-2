package ru.yandex.autotests.mainmorda.commontests.news;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.NewsBlockData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.NewsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.DEFAULT_NEWS_SIZE;
import static ru.yandex.autotests.mainmorda.data.NewsBlockData.NEWS_LANGUAGE;

/**
 * User: alex89
 * Date: 18.04.12
 * Проверка списка новостей и ссылок
 */
@Aqua.Test(title = "Главные события")
@Features({"Main", "Common", "News Block"})
@Stories("Main News")
public class NewsItemsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private NewsSteps userNews = new NewsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.newsBlock);
        user.shouldSeeElement(mainPage.newsBlock.mainNewsTab);
        userNews.switchToTab(mainPage.newsBlock.mainNewsTab);
    }

    @Test
    public void newsNumber() {
        user.shouldSeeListWithSize(mainPage.newsBlock.mainNews, equalTo(DEFAULT_NEWS_SIZE));
    }

    @Test
    public void newsNumerationByDefault() {
        userNews.shouldSeeNumeration(mainPage.newsBlock.mainNews);
    }

    @Test
    public void newsHaveCorrectSymbols() {
        userNews.shouldSeeLanguage(mainPage.newsBlock.mainNews, NEWS_LANGUAGE);
    }

    @Test
    public void noNewsDuplicates() {
        userNews.shouldNotSeeDuplicates(userNews.getNewsTexts(mainPage.newsBlock.mainNews));
    }

    @Test
    public void newsLinks() {
        userNews.shouldSeeLinks(mainPage.newsBlock.mainNewsTab,
                mainPage.newsBlock.mainNews, NewsBlockData.NEWS_LINK);
    }
}