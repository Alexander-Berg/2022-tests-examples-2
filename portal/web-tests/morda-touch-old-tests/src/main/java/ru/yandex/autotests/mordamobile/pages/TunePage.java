package ru.yandex.autotests.mordamobile.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.CheckBox;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class TunePage {
    public TunePage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Чекбокс включения/выключения саджест")
    @FindBy(xpath = "//input[@id='suggest_tune']")
    public CheckBox suggestCheckBox;

    @Name("Кнопка 'Сохранить'")
    @FindBy(xpath = "//input[@class='b-form__submit']")
    public HtmlElement saveButton;

}
