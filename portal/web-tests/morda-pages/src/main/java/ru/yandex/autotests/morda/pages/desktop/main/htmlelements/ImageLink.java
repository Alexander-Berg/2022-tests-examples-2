package ru.yandex.autotests.morda.pages.desktop.main.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/08/15
 */
public class ImageLink extends HtmlElement {

    @Name("Картинка")
    @FindBy(xpath = ".//img")
    public HtmlElement img;

}
