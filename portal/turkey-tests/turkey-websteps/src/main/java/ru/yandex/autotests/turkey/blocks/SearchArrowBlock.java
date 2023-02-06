package ru.yandex.autotests.turkey.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
@FindBy(xpath = "//td[contains(@class, 'main__item__search')]/form")
@Name("Search Arrow")
public class SearchArrowBlock extends HtmlElement {

    @Name("поле ввода")
    @FindBy(xpath = ".//input[@id='text']")
    public TextInput input;

    @Name("кнопка поиска")
    @FindBy(xpath = ".//button[@type='submit']")
    public HtmlElement submit;

    @Name("иконка клавиатуры")
    @FindBy(xpath = ".//div[contains(@class,' keyboard-loader')]/i")
    public HtmlElement keyboard;

    @Name("саджест")
    @FindBy(xpath = "//div[contains(@class,'suggest') and contains(@class,'popup')]")
    public HtmlElement suggest;

    @Name("lr")
    @FindBy(xpath = ".//input[@type='hidden' and @name='lr']")
    public HtmlElement lr;
}
