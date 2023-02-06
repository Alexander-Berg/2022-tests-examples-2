package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок афиши")
@FindBy(xpath = "//div[contains(@class, 'b-widget b-apps')]")
public class AppsBlock extends HtmlElement {
    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Приложения")
    @FindBy(xpath = ".//div[contains(@class, 'b-apps__icon')]")
    public List<HtmlElement> apps;

    @Name("Все приложения")
    @FindBy(xpath = ".//a[contains(@class, 'b-apps__more')]")
    public HtmlElement allApps;
}
