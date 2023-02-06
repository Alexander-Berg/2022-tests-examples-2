package ru.yandex.autotests.mordacom.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

/**
 * User: eoff
 * Date: 16.11.12
 */
public class HomePage {

    public HomePage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Header")
    public HeaderBlock headerBlock;

    @Name("Логотип")
    @FindBy(xpath = ".//div[contains(@class,'logo')]//div[contains(@class,'logo__image_bg')]")
    public HtmlElement yandexLogo;

    @Name("Футер")
    public FooterBlock footerBlock;

    @Name("Поисковая форма")
    public SearchArrowBlock search;

    @Name("Блок табов")
    public TabsBlock tabsBlock;

    @Name("Блок стран")
    public CountriesBlock countriesBlock;

    @Name("Виртуальная клавиатура")
    public VirtualKeyboard keyboard;

    @Name("Элементы с BADID")
    @FindBy(xpath = "//*[contains(@onmousedown, 'BADID')]")
    public List<HtmlElement> elementsWithBadId;
}
