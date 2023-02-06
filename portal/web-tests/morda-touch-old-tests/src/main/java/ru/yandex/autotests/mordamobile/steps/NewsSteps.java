package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.blocks.NewsBlock;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ch.lambdaj.Lambda.on;
import static ru.yandex.autotests.mordamobile.data.NewsData.Category;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class NewsSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps userSteps;

    public NewsSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public void selectCategory(Category category) {
        NewsBlock.NewsCategory categoryElement =
                userSteps.findFirst(homePage.newsBlock.allCategories,
                        on(NewsBlock.NewsCategory.class),
                        hasText(category.getName()));
        userSteps.selectElement(categoryElement);
    }

    @Step
    public void shouldSeeNewsLinks(Category category) {
        for (int i = 0; i < homePage.newsBlock.allNews.size(); i++) {
            HtmlElement element = homePage.newsBlock.allNews.get(i);
            userSteps.shouldSeeLink(element, category.getSearchLink());
            userSteps.opensPage(CONFIG.getBaseURL());
            selectCategory(category);
        }
    }
}
