package ru.yandex.autotests.mainmorda.blocks.all;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 26.02.2015.
 */
@Name("Хедер страницы всех сервисов")
@FindBy(xpath = "//div[contains(@class, 'b-line__header')]")
public class AllServicesHeader extends HtmlElement {
    @Name("Ссылка на мобильные приложения")
    @FindBy (xpath = "//div[contains(@class,'header__right b-inline')]//a[1]")
    public HtmlElement mobileLink;

    @Name("Ссылка на программы для компьютера")
    @FindBy (xpath = "//div[contains(@class,'header__right b-inline')]//a[2]")
    public HtmlElement programsLink;

    @Name("Ссылка на главную")
    @FindBy (xpath = "//div[contains(@class,'header__left b-inline')]//a[contains(@class,'link')]")
    public HtmlElement mainPageLink;
}