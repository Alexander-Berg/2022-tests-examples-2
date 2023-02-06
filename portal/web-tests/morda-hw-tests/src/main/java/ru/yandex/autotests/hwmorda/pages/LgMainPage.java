package ru.yandex.autotests.hwmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: alex89
 * Date: 12.09.12
 */
public class LgMainPage {
    public LgMainPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Логотип")
    @FindBy(xpath = ".//div[@class='header']//div[@class='header__logo']")
    public HtmlElement logo;

    @Name("Виджет Погода")
    @FindBy(xpath = ".//div[@nav-event='weather'and contains(.,'Погода')]/div[@class='wdgt__container']")
    public HtmlElement weatherWidget;

    @Name("Виджет Новости")
    @FindBy(xpath = ".//div[@nav-event='topnews'and contains(.,'Новости')]/div[@class='wdgt__container']")
    public HtmlElement newsWidget;

    @Name("Виджет Котировки")
    @FindBy(xpath = ".//div[@nav-event='stocks'and contains(.,'Котировки')]/div[@class='wdgt__container']")
    public HtmlElement stocksWidget;

    @Name("Виджет Телепрограмма")
    @FindBy(xpath = ".//div[@nav-event='tv' and contains(.,'Телепрограмма')]/div[@class='wdgt__container']")
    public HtmlElement tvWidget;

    @Name("Виджет Фото дня")
    @FindBy(xpath = ".//div[@nav-event='fotki'and contains(.,'Фото дня')]/div[@class='wdgt__container']")
    public HtmlElement photoWidget;

    @Name("Фото в виджете Фото дня")
    @FindBy(xpath = ".//div[@nav-event='fotki'and contains(.,'Фото дня')]/div[@class='wdgt__container']" +
            "//div[contains(@class,'img')]")
    public HtmlElement photoInPhotoWidget;

    @Name("Виджет Пробки")
    @FindBy(xpath = ".//div[@nav-event='traffic'and contains(.,'Пробки')]/div[@class='wdgt__container']")
    public HtmlElement trafficWidget;

    public LgFooterPanel footerPanel;
}
