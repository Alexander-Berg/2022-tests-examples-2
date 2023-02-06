package ru.yandex.autotests.mordacom.pages;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Name("Попап переключалки языков")
@FindBy(xpath = "//div[contains(@class, 'popup__content')]//div[contains(@class, 'langswitch__list')]")
public class LangSwitcherPopupBlock extends HtmlElement {

    @Name("Доступный язык")
    @FindBy(xpath = ".//a")
    public HtmlElement availableLanguage;

    @Name("Текущий язык")
    @FindBy(xpath = ".//span[contains(@class, 'langswitch__current')]")
    public HtmlElement currentLanguage;
}
