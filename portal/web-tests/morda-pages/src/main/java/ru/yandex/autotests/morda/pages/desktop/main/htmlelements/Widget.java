package ru.yandex.autotests.morda.pages.desktop.main.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.matchers.common.IsElementDisplayedMatcher;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/11/15
 */
public class Widget<T extends WidgetSetupPopup> extends HtmlElement {

    public WidgetControls widgetControls;
    public WidgetAddControls widgetAddControls;

    protected T getSetupPopup()
    {
        throw new RuntimeException("Override getSetupPopup() method");
    }

    @Step("Open widget settings")
    public T setup() {
        shouldSee(widgetControls);
        widgetControls.openWidgetSettings();
        return getSetupPopup();
    }

    @Step("Remove widget")
    public void remove() {
        shouldSee(widgetControls);
        widgetControls.removeWidget();
    }

    public String getId() {
        return this.getAttribute("id").replace("wd-wrapper-", "");
    }

    @Name("Widget controls")
    @FindBy(xpath = ".//div[contains(@class, 'widget__control')]")
    public static class WidgetControls extends HtmlElement {

        @Name("Widget settings icon")
        @FindBy(xpath = ".//span[contains(@class, 'widget__prefs')]")
        public HtmlElement setup;

        @Name("Widget remove icon")
        @FindBy(xpath = ".//span[contains(@class, 'widget__remove')]")
        public HtmlElement remove;

        public void openWidgetSettings() {
            shouldSee(setup);
            clickOn(setup);
        }

        public void removeWidget() {
            shouldSee(remove);
            clickOn(remove);
        }
    }

    @Name("Контролы добавления виджета")
    @FindBy(xpath = ".//div[contains(@class, 'widget__buttons')]")
    public static class WidgetAddControls extends HtmlElement {

        @Name("Кнопка \"Отмена\"")
        @FindBy(xpath = ".//button[contains(@class, 'widget__reject')]")
        public HtmlElement cancel;

        @Name("Кнопка \"Сохранить\"")
        @FindBy(xpath = ".//button[contains(@class, 'widget__accept')]")
        public HtmlElement save;

        @Step("Cancel widget addition")
        public void cancelAddition() {
            assertThat(cancel, exists());
            assertThat(cancel, IsElementDisplayedMatcher.isDisplayed());
            cancel.click();
        }

        @Step("Accept widget addition")
        public void acceptAddition() {
            assertThat(save, exists());
            assertThat(save, IsElementDisplayedMatcher.isDisplayed());
            save.click();
        }
    }
}
