package ru.yandex.autotests.mainmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.CheckBox;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff
 * Date: 29.01.13
 */
public class TuneBannerPage {
    public TuneBannerPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Чекбокс показа баннера")
    @FindBy(xpath = "//span[@class='b-form-checkbox__inner']//input")
    public CheckBox noBannerCheckbox;

    @Name("Кнопка сохранения города")
    @FindBy(xpath = "//input[@type='submit']")
    public HtmlElement saveButton;
}
