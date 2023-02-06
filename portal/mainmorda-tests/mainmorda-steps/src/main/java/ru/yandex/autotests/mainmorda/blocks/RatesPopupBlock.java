package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */

@Name("Попап котировок")
@FindBy(xpath = "//div[contains(@class,'inline-stocks__popup-wrap')]")
public class RatesPopupBlock extends HtmlElement {

    @Name("Ссылки котировок")
    @FindBy(xpath = ".//div[contains(concat(' ',@class,' '),' inline-stocks__popup ')]//a")
    public List<HtmlElement> ratesLinks;

    @Name("Крестик закрытия")
    @FindBy(xpath = ".//div[contains(@class,'popup__close')]")
    public HtmlElement close;
}
