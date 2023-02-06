package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 24.12.2014.
 */

@Name("блок метро")
@FindBy(xpath = "//div [@class='b-widget b-metro']")
public class MetroBlock extends HtmlElement {
    @Name("ссылка на метро")
    @FindBy(xpath = ".//a [contains(@class,'b-link')]")
    public HtmlElement metroLink;

    @Name("текст: \"схема метро\"")
    @FindBy(xpath = ".//div[contains(@class,'b-metro__text')]")
    public HtmlElement metroText;

    @Name("иконка метро")
    @FindBy(xpath = ".//div[contains(@class,'b-metro__icon')]")
    public HtmlElement metroIcon;
}
