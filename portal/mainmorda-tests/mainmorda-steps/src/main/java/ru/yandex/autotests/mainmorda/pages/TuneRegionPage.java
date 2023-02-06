package ru.yandex.autotests.mainmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.CheckBox;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff
 * Date: 29.01.13
 */
public class TuneRegionPage {
    public TuneRegionPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Чекбокс автоматического определения региона")
    @FindBy(xpath = "//input[@id='auto']")
    public CheckBox auto;

    @Name("Поле ввода города")
    @FindBy(xpath = "//input[@name='region']")
    public TextInput input;

    @Name("Саджест с городом")
    @FindBy(xpath = "//ul[contains(@class, 'b-form-input__popup-items')]//li[1]")
    public HtmlElement suggest;

    @Name("Кнопка сохранения города")
    @FindBy(xpath = "//input[@type='submit']")
    public HtmlElement saveButton;
}
