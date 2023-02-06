package ru.yandex.autotests.hwmorda.pages;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.hwmorda.data.RubricButton;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 12.09.12
 */
@FindBy(xpath = "//td[@class='l-page__left']")
@Name("Кнопки переключения рубрик-сервисов")
public class LgRubricsPanel extends HtmlElement {
    @Name("Кнопка 'В начало'")
    @FindBy(xpath = ".//div[@nav-event='index'and contains(.,'начало')]")
    public RubricButton homeButton;

    @Name("Рубрика 'Погода'")
    @FindBy(xpath = ".//div[@nav-event='weather'and contains(.,'Погода')]")
    public RubricButton weatherButton;

    @Name("Рубрика 'Новости'")
    @FindBy(xpath = ".//div[@nav-event='topnews'and contains(.,'Новости')]")
    public RubricButton newsButton;

    @Name("Рубрика 'Котировки'")
    @FindBy(xpath = ".//div[@nav-event='stocks'and contains(.,'Котировки')]")
    public RubricButton stocksButton;

    @Name("Рубрика 'Телепрограмма'")
    @FindBy(xpath = ".//div[@nav-event='tv' and contains(.,'Телепрограмма')]")
    public RubricButton tvButton;

    @Name("Рубрика 'Фото дня'")
    @FindBy(xpath = ".//div[@nav-event='fotki'and contains(.,'Фото дня')]")
    public RubricButton photoButton;

    @Name("Рубрика 'Пробки'")
    @FindBy(xpath = ".//div[@nav-event='traffic'and contains(.,'Пробки')]")
    public RubricButton trafficButton;
}