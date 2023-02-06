package ru.yandex.autotests.mordacom.pages;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff
 * Date: 20.11.12
 */
@Name("Блок стран")
@FindBy(xpath = "//div[contains(@class,'b-line__worldwide')]")
public class CountriesBlock extends HtmlElement {

    @Name("Текст 'Yandex in'")
    @FindBy(xpath = ".//span[contains(@class, 'worldwide__title')]")
    public HtmlElement yandexInText;

    @Name("Ссылки на страны")
    @FindBy(xpath = ".//span[contains(@class, 'worldwide__list')]//a")
    public List<CountryItem> allItems;

    public static class CountryItem extends HtmlElement {
        @Name("Название страны")
        @FindBy(xpath = ".//span")
        public HtmlElement countryText;

        @Name("Флаг страны")
        @FindBy(xpath = ".//img")
        public HtmlElement countryImg;
    }


}
