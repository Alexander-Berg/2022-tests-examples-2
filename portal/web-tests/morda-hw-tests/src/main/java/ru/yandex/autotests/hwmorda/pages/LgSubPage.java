package ru.yandex.autotests.hwmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: alex89
 * Date: 13.09.12
 */
public class LgSubPage {
    public LgSubPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private static final String RIGHT_AREA_XPATH = ".//td[contains(@class,'right')]";

    @Name("Логотип")
    @FindBy(xpath = ".//div[@class='header']//div[@class='header__logo']")
    public HtmlElement logo;

    public LgRubricsPanel rubricsPanel;

    @Name("Виджет Погода")
    @FindBy(xpath = RIGHT_AREA_XPATH +
            "//div[contains(@class,'wdgt__container') and contains(.,'Погода')]//div[@class='page__weather']")
    public HtmlElement weatherWidget;

    @Name("Виджет Новости")
    @FindBy(xpath = RIGHT_AREA_XPATH +
            "//div[contains(@class,'wdgt__container') and contains(.,'Новости')]//div[@class='page__topnews-category']")
    public HtmlElement newsWidget;

    @Name("Виджет Новости(режим местных новостей)")
    @FindBy(xpath = RIGHT_AREA_XPATH +
            "//div[contains(@class,'wdgt__container') and contains(.,'Новости')]" +
            "//div[contains(@class,'page__topnews-local')]")
    public HtmlElement regNewsWidget;

    @Name("Виджет Котировки")
    @FindBy(xpath = RIGHT_AREA_XPATH +
            "//div[contains(@class,'wdgt__container') and contains(.,'Котировки')]//div[@class='page__stocks']")
    public HtmlElement stocksWidget;

    @Name("Виджет Телепрограмма")
    @FindBy(xpath = RIGHT_AREA_XPATH +
            "//div[contains(@class,'wdgt__container') and contains(.,'Телепрограмма')]//div[@class='wdgt__content']")
    public HtmlElement tvWidget;

    @Name("Виджет Фото дня")
    @FindBy(xpath = RIGHT_AREA_XPATH +
            "//div[contains(@class,'wdgt__container') and contains(.,'Фото дня')]//div[@class='page__fotki']")
    public HtmlElement photoWidget;

    @Name("Виджет Пробки")
    @FindBy(xpath = RIGHT_AREA_XPATH +
            "//div[contains(@class,'wdgt__container') and contains(.,'Пробки')]//div[@class='page__traffic']")
    public HtmlElement trafficWidget;

    public LgFooterPanel footerPanel;

    @Name("Режим Сдайд-шоу")
    @FindBy(xpath = ".//div[@class='slideshow' and contains(.,'Закрыть слайд-шоу')]" +
            "//img[contains(@src,'fotki.yandex.net/')]")
    public HtmlElement slideShowMode;

    @Name("Любое место на экране (для закрытия слайд-шоу)")
    @FindBy(xpath = ".//body")
    public HtmlElement anyPlace;
}
