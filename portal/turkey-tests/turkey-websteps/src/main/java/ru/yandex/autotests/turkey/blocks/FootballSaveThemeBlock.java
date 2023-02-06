package ru.yandex.autotests.turkey.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * Author  <poluektov@yandex-team.ru>
 * on 28.11.2014.
 */

@Name("футбольный 'Сохранить/Нет' блок")
@FindBy(xpath = "//div[contains(@class,'popup_to_top')]//div[@class='popup__content']")
public class FootballSaveThemeBlock extends HtmlElement {
    @Name("Текст")
    @FindBy(xpath = ".//div[@class='reset__popup-text']")
    public HtmlElement popUpText;

    @Name("Кнопка 'не сохранять'")
    @FindBy(xpath = ".//a[contains(@class, 'button_theme_normal')]")
    public HtmlElement popUpCancelButton;

    @Name("Кнопка 'сохранить'")
    @FindBy(xpath = ".//a[contains(@class, 'button_theme_action')]")
    public HtmlElement popUpSaveButton;
}
