package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Информер погоды")
@FindBy(xpath = "//li[contains(@class, 'b-informer_type_weather')]")
public class WeatherBlock extends HtmlElement {
    @Name("Иконка")
    @FindBy(xpath = ".//img")
    public HtmlElement icon;

    @Name("Заголовок")
    @FindBy(xpath = ".//div[contains(@class,'b-informer__title')]")
    public HtmlElement title;

    @Name("Ссылка информера")
    @FindBy(xpath = ".//a")
    public HtmlElement weatherLink;

    @Name("Прогноз температуры")
    @FindBy(xpath = ".//div[@class='b-informer__data']")
    public HtmlElement forecast;
}
