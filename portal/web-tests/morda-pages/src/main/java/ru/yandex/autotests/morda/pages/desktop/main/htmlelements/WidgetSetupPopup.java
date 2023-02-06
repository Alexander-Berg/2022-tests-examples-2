package ru.yandex.autotests.morda.pages.desktop.main.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldNotSee;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;

@Name("Widget settings")
@FindBy(xpath = "//div[@id='widget_pref_form']")
public class WidgetSetupPopup extends HtmlElement {

    public WidgetSetupControls widgetSetupControls;

    @Name("Close cross")
    @FindBy(xpath = ".//i[contains(@class, 'popup__close')]")
    public HtmlElement close;

    @Step("Close widget settings")
    public void close() {
        shouldSee(close);
        clickOn(close);
        shouldNotSee(this);
    }

    @Step("Reset widget settings")
    public void reset() {
        shouldSee(widgetSetupControls);
        shouldSee(widgetSetupControls.reset);
        clickOn(widgetSetupControls.reset);
        shouldNotSee(this);
    }

    @Step("Cancel widget settings")
    public void cancel() {
        shouldSee(widgetSetupControls);
        shouldSee(widgetSetupControls.cancel);
        clickOn(widgetSetupControls.cancel);
        shouldNotSee(this);
    }

    @Step("Save widget settings")
    public void save() {
        shouldSee(widgetSetupControls);
        shouldSee(widgetSetupControls.save);
        clickOn(widgetSetupControls.save);
        shouldNotSee(this);
    }

    @Name("Widget settings controls")
    @FindBy(xpath = ".//div[contains(@class, 'b-wdgt-preferences__controls')]")
    public static class WidgetSetupControls extends HtmlElement {

        @Name("Reset button")
        @FindBy(xpath = ".//button[contains(@class, 'b-wdgt-preferences__reset')]")
        public HtmlElement reset;

        @Name("Close button")
        @FindBy(xpath = ".//button[contains(@class, 'b-wdgt-preferences__cancel')]")
        public HtmlElement cancel;

        @Name("Ok button")
        @FindBy(xpath = ".//button[contains(@class, 'b-wdgt-preferences__save')]")
        public HtmlElement save;
    }
}