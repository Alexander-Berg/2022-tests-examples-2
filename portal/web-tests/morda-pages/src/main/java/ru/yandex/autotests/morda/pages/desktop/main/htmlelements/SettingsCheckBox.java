package ru.yandex.autotests.morda.pages.desktop.main.htmlelements;

import org.hamcrest.Matchers;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.CheckBox;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.matchers.TypifiedElementMatchers;

import static java.lang.String.format;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;
import static ru.yandex.autotests.morda.steps.WebElementSteps.withWait;

public class SettingsCheckBox extends HtmlElement{

    @Name("Чекбокс")
    @FindBy(xpath = ".//input")
    public CheckBox input;

    @Step("Check \"{0}\"")
    public void check(){
        shouldSee(this);
        input.select();
        String errorMessage = format("\"%s\" must be selected", input);
        assertThat(errorMessage, input, withWait(TypifiedElementMatchers.isSelected()));
    }

    @Step("Uncheck \"{0}\"")
    public void uncheck(){
        shouldSee(this);
        input.deselect();
        String errorMessage = format("\"%s\" must not be selected", input);
        assertThat(errorMessage, input, withWait(not(TypifiedElementMatchers.isSelected())));
    }

    @Step
    public void shouldNotBeChecked(){
        String errorMessage = format("\"%s\" must be not selected", input);
        assertThat(errorMessage, input, withWait(Matchers.not(TypifiedElementMatchers.isSelected())));
    }

    @Step
    public void shouldBeChecked(){
        String errorMessage = format("\"%s\" must be selected", input);
        assertThat(errorMessage, input, withWait(TypifiedElementMatchers.isSelected()));
    }

}
