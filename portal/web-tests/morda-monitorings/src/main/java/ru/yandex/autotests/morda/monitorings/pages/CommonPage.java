package ru.yandex.autotests.morda.monitorings.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/11/14
 */
public class CommonPage {
    public CommonPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Строка поиска")
    @FindBy(xpath = "//input[@id='text' or @name='text']")
    public TextInput input;

}
