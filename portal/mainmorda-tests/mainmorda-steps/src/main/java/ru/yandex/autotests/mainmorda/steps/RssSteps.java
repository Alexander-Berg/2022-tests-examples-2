package ru.yandex.autotests.mainmorda.steps;

import org.hamcrest.Matcher;
import org.hamcrest.text.IsEmptyString;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.autotests.mainmorda.blocks.RssWidget;
import ru.yandex.autotests.mainmorda.blocks.SettingsSelect;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.isDisplayed;

/**
 * User: eoff
 * Date: 04.02.13
 */
public class RssSteps {
    private static final int NUMBER_OF_ATTEMPT = 25;

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private MainPage mainPage;

    public RssSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.mainPage = new MainPage(driver);
    }

    @Step
    public void shouldSeeSelectWithOptions(SettingsSelect select, List<Matcher<String>> options) {
        List<HtmlElement> list = select.getOptionsAsHtmlElements();
        userSteps.shouldSeeListWithSize(list, equalTo(options.size()));
        int i = 0;
        for (HtmlElement element : list) {
            userSteps.shouldSeeElementWithText(element, options.get(i++));
        }
    }

    @Step
    public void shouldSeeDescriptionItem(WrapsElement description) {
        assertThat(description + " отсутствует в верстке страницы!", description,
                withWaitFor(exists()));
        for (int i = 0; !description.getWrappedElement().isDisplayed() && i < NUMBER_OF_ATTEMPT; i++) {
            ((JavascriptExecutor) driver)
                    .executeScript("document.getElementsByClassName('w-rss__arrow_type_down')[0].click();");
        }
        assertThat(description + " не отображается на странице!", description,
                withWaitFor(isDisplayed()));
    }

    @Step
    public void shouldSeeDescriptions() {
        userSteps.shouldSeeListWithSize(mainPage.rssWidget.rssOptions, greaterThan(0));
        RssWidget.RssOption option = mainPage.rssWidget.rssOptions.get(0);
        shouldSeeDescriptionItem(option.description);
        userSteps.shouldSeeElementWithText(option.description, not(IsEmptyString.isEmptyOrNullString()));
    }

    @Step
    public void shouldNotSeeDescriptions() {
        for (RssWidget.RssOption option : mainPage.rssWidget.rssOptions) {
            userSteps.shouldNotSeeElement(option.description);
        }
    }

    @Step
    public void shouldSeeImages() {
//        Assert.assertThat("Изображений не видно!", mainPage.rssWidget.rssOptions,
//                hasItem(withImage()));
    }

    @Step
    public void shouldNotSeeImages() {
//        Assert.assertThat("Изображений не должно быть видно!", mainPage.rssWidget.rssOptions,
//                everyItem(not(withImage())));
    }
}
