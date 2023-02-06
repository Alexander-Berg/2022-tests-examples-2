package ru.yandex.autotests.mordamobile.blocks.all;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

@Name("Хедер страницы всех сервисов")
@FindBy(xpath = "//div[contains(@class, 'b-line__header')]")
public class AllServicesPageHeader extends HtmlElement {
    @Name("Логотип")
    @FindBy(xpath = ".//div[contains(@class,'header__top')]//a[contains(@class,'link')]")
    public HtmlElement logo;

    @Name("Ссылка на мобильные приложения")
    @FindBy(xpath = ".//a[contains(@class, 'tab_name_apps')]")
    public HtmlElement mobileAppsLink;

    @Name("Текст 'Мобильные сайты'")
    @FindBy(xpath = ".//div[contains(@class, 'tab_name_mobile')]")
    public HtmlElement mobileSitesText;
}