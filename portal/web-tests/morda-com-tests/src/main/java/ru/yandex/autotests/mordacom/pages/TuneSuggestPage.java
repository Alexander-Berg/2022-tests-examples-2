package ru.yandex.autotests.mordacom.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.CheckBox;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: ivannik
 * Date: 15.05.2014
 */
public class TuneSuggestPage {
    public TuneSuggestPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Чекбокс включения/выключения саджеста")
    @FindBy(xpath = "//span[contains(@class,'checkbox_type_suggest')]//input")
    public CheckBox suggestCheckBox;

    @Name("Кнопка сохранения")
    @FindBy(xpath = "//input[@class='b-form-button__input'][@type='submit']")
    public HtmlElement saveButton;
}
