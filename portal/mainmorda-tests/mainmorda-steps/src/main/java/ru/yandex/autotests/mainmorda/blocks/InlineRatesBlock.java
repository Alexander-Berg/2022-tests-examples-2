package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: ivannik
 * Date: 19.10.14
 */

@FindBy(xpath = "//div[contains(@class,'inline-stocks')]")
@Name("Блок котировок под новостями")
public class InlineRatesBlock extends HtmlElement {

    @Name("Ссылки котировок")
    @FindBy(xpath = ".//a")
    public List<HtmlElement> ratesLinks;

    @Name("Кнопка 'ещё'")
    @FindBy(xpath = ".//a[contains(@class,'inline-stocks__more')]")
    public HtmlElement moreStocksButton;

    @Name("Кнопка 'Переместить вниз'")
    @FindBy(xpath = ".//a[contains(@class,'toggle-down')]")
    public HtmlElement toggleDownButton;
}
