package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 28.09.12
 * Класс для работы с табами Новостей,Тв,Афиши.
 */
public class TvAfishaNewsTab extends HtmlElement {

    @Name("Ссылка в выборе табы")
    @FindBy(xpath = ".//a")
    public HtmlElement tabLink;

    @Override
    public boolean isSelected() {
        return getWrappedElement().getAttribute(HtmlAttribute.CLASS.toString()).contains("_active_yes");
    }
}
