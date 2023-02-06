package ru.yandex.autotests.mordatmplerr.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29.04.14
 */
public class HomePage {
    public HomePage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Поле ввода")
    @FindBy(xpath = "//input[@name='text']")
    public TextInput input;
}
