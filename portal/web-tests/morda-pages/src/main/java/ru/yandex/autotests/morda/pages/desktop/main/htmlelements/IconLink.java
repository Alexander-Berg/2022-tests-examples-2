package ru.yandex.autotests.morda.pages.desktop.main.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/08/15
 */
public class IconLink extends HtmlElement {

    @Name("Иконка")
    @FindBy(xpath = ".//i")
    public HtmlElement i;

}
