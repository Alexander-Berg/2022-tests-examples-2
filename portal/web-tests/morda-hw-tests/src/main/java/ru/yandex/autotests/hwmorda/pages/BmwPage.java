package ru.yandex.autotests.hwmorda.pages;


import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.hwmorda.data.RubricButton;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

/**
 * User: alex89
 * Date: 12.09.12
 */

public class BmwPage {
    public BmwPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Логотип")
    @FindBy(xpath = ".//a[contains(@class,'header__logo')]")
    public HtmlElement logo;

    @Name("Ссылка с названием регионов")
    @FindBy(xpath = ".//table[contains(@class,'city')]//a[contains(@href,'/bmw/tune')]")
    public HtmlElement regionName;


    @Name("Рубрика 'Пробки'")
    @FindBy(xpath = ".//a[contains(@class,'nav__item') and contains(@class,'traffic')]")
    public RubricButton trafficButton;

    @Name("Рубрика 'Погода'")
    @FindBy(xpath = ".//a[contains(@class,'nav__item') and contains(@class,'weather')]")
    public RubricButton weatherButton;

    @Name("Рубрика 'Новости'")
    @FindBy(xpath = ".//a[contains(@class,'nav__item') and contains(@class,'topnews')]")
    public RubricButton newsButton;

    @Name("Рубрика 'Котировки'")
    @FindBy(xpath = ".//span[contains(@class,'nav__item') and contains(@class,'stocks')]")
    public RubricButton stocksArea;


    @Name("Виджет Погода")
    @FindBy(xpath = ".//div[@id='weather-full']")
    public HtmlElement weatherWidget;

    @Name("Виджет Новости")
    @FindBy(xpath = ".//div[@id='full-news']")
    public HtmlElement newsWidget;

    @Name("Виджет Пробки")
    @FindBy(xpath = ".//div[@class='map']")
    public HtmlElement trafficWidget;

    @Name("Под-страница 'Выберите город России'")
    @FindBy(xpath = ".//div[@class='geo']")
    public HtmlElement changeRegionWidget;

    @Name("Регион №")
    @FindBy(xpath = ".//div[@class='geo']//a[contains(@href,'city') and not (contains(@href,'drop'))]")
    public List<HtmlElement> regions;
}
