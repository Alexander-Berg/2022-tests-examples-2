package ru.yandex.autotests.hwmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * Created with IntelliJ IDEA.
 * User: lipka
 * Date: 03.04.13
 * Time: 15:45
 * To change this template use File | Settings | File Templates.
 */
public class FotkiPage {
    public FotkiPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Фото дня")
    @FindBy(xpath = "//a[contains(@class,'photo-well-image_is-visible')]")
    public HtmlElement foto;
}



