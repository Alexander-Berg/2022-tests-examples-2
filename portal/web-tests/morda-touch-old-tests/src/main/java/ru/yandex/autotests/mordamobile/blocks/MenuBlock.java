package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 25.04.13
 */
@Name("Выпадающее меню")
@FindBy(xpath = "//div[contains(@class, 'b-head-sideslide__right')]")
public class MenuBlock extends HtmlElement {

    @Name("Заголовок меню")
    @FindBy(xpath = ".//h3")
    public HtmlElement title;

    @Name("табы ")
    @FindBy(xpath = ".//a")
    public List<HtmlElement> allTabs;
}
