package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок региона")
@FindBy(xpath = "//div[contains(@class, 'b-region b-region-exact')]")
public class GeoBlock extends HtmlElement {
    @Name("Иконка автоматического определения местоположения")
    @FindBy(xpath = ".//div[@class='b-region__locate']")
    public HtmlElement autoLocateIcon;

    @Name("Регион")
    @FindBy(xpath = ".//span[@class='b-region__city']")
    public HtmlElement region;
}
