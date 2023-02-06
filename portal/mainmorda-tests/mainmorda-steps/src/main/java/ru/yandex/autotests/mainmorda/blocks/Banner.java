package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 06.12.12
 */

@Name("Баннер")
public class Banner extends HtmlElement {

    @Name("Flash объект")
    @FindBy(xpath = ".//object")
    public HtmlElement flashObject;

    @Name("Параметр movie баннера")
    @FindBy(xpath = ".//param[@name='movie']")
    public HtmlElement movieParam;

    @Name("Параметр flashvars баннера")
    @FindBy(xpath = ".//param[@name='flashvars']")
    public HtmlElement flashParam;
}
