package ru.yandex.autotests.turkey.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: ivannik
 * Date: 23.10.13
 * Time: 20:46
 */
public class TuneRedirectPage {
    public TuneRedirectPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Чекбокс Отключить редирект")
    @FindBy(xpath = "//input[@class = 'checkbox__control']")
    public HtmlElement redirectCheckbox;

    @Name("Кнопка сохранить")
    @FindBy(xpath = "//button[contains(@class, 'form__save')]")
    public HtmlElement saveButton;
}
