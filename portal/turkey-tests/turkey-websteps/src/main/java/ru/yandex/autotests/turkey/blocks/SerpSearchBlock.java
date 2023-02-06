package ru.yandex.autotests.turkey.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
@FindBy(xpath = "//form[contains(@class,'search')]")
@Name("Serp search Arrow")
public class SerpSearchBlock extends HtmlElement {
    @Name("поле ввода")
    @FindBy(xpath = ".//input[@name='text']")
    public TextInput input;
}
