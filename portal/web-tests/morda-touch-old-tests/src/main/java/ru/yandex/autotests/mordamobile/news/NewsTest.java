package ru.yandex.autotests.mordamobile.news;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.blocks.NewsBlock;
import ru.yandex.autotests.mordamobile.data.NewsData;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.mordamobile.steps.NewsSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ch.lambdaj.Lambda.on;
import static ru.yandex.autotests.mordamobile.data.NewsData.TITLE_LINK;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блок новостей")
@RunWith(Parameterized.class)
@Features("News")
public class NewsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private NewsSteps userNews = new NewsSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(NewsData.Category.values());
    }

    private NewsData.Category category;

    public NewsTest(NewsData.Category category) {
        this.category = category;
    }

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.newsBlock);
        userNews.selectCategory(category);
    }

    @Test
    public void newsTitle() {
        user.shouldSeeLink(homePage.newsBlock.title, TITLE_LINK);
    }

    @Test
    public void newsLinks() {
        userNews.shouldSeeNewsLinks(category);
    }

    @Test
    public void categoryLink() throws InterruptedException {
        NewsBlock.NewsCategory categoryElement =
                user.findFirst(homePage.newsBlock.allCategories,
                        on(NewsBlock.NewsCategory.class),
                        hasText(category.getName()));
        Thread.sleep(1000);
        user.clicksOn(categoryElement);
        user.shouldSeePage(category.getUrl());
    }
}
