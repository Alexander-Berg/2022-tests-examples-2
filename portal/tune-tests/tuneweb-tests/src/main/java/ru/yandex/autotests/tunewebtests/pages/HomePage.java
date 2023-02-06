package ru.yandex.autotests.tunewebtests.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06.05.13
 */
public class HomePage {
    public HomePage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @FindBy(xpath = "//a[@href]")
    public List<HtmlElement> allLinks;
}
