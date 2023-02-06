package ru.yandex.autotests.widgets.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.Properties;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.widgets.data.SearchData.Category;
import static ru.yandex.autotests.widgets.data.SearchData.WIDGETS_NUMBER_MATCHER;
import static ru.yandex.autotests.widgets.pages.WidgetPage.CategoryElement;
import static ru.yandex.autotests.widgets.pages.WidgetPage.TagElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.07.13
 */
public class CategorySteps {
    private static final Properties CONFIG = new Properties();

    private CommonMordaSteps userSteps;
    private WidgetPage widgetPage;
    private WebDriver driver;

    public CategorySteps(WebDriver driver) {
        this.driver = driver;
        this.widgetPage = new WidgetPage(driver);
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step
    public TagElement findTagOnPage(List<TagElement> allTags, String tag) {
        for (TagElement element : allTags) {
            if (element.getText().equals(tag)) {
                return element;
            }
        }
        fail("Тег " + tag + " не найден");
        return null;
    }

    @Step
    public void shouldSeeTag(List<TagElement> allTags, String tag) {
        TagElement element = findTagOnPage(allTags, tag);
        if (element != null) {
            String href = element.getAttribute(HREF.toString());
            userSteps.clicksOn(element);
            userSteps.shouldSeePage(href);
            element = findTagOnPage(allTags, tag);
            userSteps.shouldSeeElementIsSelected(element);
            userSteps.shouldSeeElement(widgetPage.title);
            userSteps.shouldSeeElementWithText(widgetPage.title, equalTo(tag));
            userSteps.shouldSeeElement(widgetPage.widgetsAmount);
            userSteps.shouldSeeElementWithText(widgetPage.widgetsAmount, WIDGETS_NUMBER_MATCHER);
            userSteps.shouldSeeListWithSize(widgetPage.allWidgets, greaterThan(0));
        }
    }


    @Step
    public CategoryElement findCategoryOnPage(List<CategoryElement> allCategories, Category category) {
        for (CategoryElement element : allCategories) {
            if (category.getText(CONFIG.getLang()).matches(element.getText())) {
                return element;
            }
        }
        fail("Категория " + category.getText(CONFIG.getLang()) + " не найдена");
        return null;
    }

    @Step
    public void shouldSeeCategory(List<CategoryElement> allCategories, Category category) {
        CategoryElement element = findCategoryOnPage(allCategories, category);
        if (element != null) {
            userSteps.shouldSeeElement(element.link);
            userSteps.shouldSeeLink(element.link, category.getLink(CONFIG.getBaseURL(), CONFIG.getLang()));
            userSteps.shouldSeeElement(widgetPage.title);
            userSteps.shouldSeeElementWithText(widgetPage.title,
                    category.getText(CONFIG.getLang()));
            userSteps.shouldSeeElement(widgetPage.widgetsAmount);
            userSteps.shouldSeeElementWithText(widgetPage.widgetsAmount, WIDGETS_NUMBER_MATCHER);
            userSteps.shouldSeeListWithSize(widgetPage.allWidgets, greaterThan(0));
        }
    }

    @Step
    public void shouldSeeCategorySelects(List<CategoryElement> allCategories, Category category) {
        CategoryElement element = findCategoryOnPage(allCategories, category);
        if (element != null) {
            userSteps.clicksOn(element);
            userSteps.shouldSeePage(category.getUrl(CONFIG.getBaseURL()));
            element = findCategoryOnPage(allCategories, category);
            userSteps.shouldSeeElementIsSelected(element);
        }
    }
}
