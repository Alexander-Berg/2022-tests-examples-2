package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * Created with IntelliJ IDEA.
 * User: lipka
 * Date: 01.12.12
 * Time: 12:12
 * To change this template use File | Settings | File Templates.
 */
@Name("Настройки новостей")
@FindBy(xpath = "//div[@id='widget_pref_form']")
public class WeatherSettingsMenu extends WidgetSettings {
    @Name("Выпадушка выбора региона")
    @FindBy(xpath = ".//input[@class='geo']")
    public TextInput regionInput;

    @Name("Подпись у выпадушки выбора региона")
    @FindBy(xpath = ".//div[@class='label']")
    public HtmlElement regionLabel;

    @Name("Саджест")
    @FindBy(xpath = ".//div[@class='suggest']")
    public HtmlElement suggest;

    @Name("Первый саджест")
    @FindBy(xpath = ".//div[@class='suggest']/a[1]")
    public HtmlElement firstSuggest;
}
