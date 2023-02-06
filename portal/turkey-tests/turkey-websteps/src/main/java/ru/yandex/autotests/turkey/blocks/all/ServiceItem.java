package ru.yandex.autotests.turkey.blocks.all;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 26.02.2015.
 */
public class ServiceItem extends HtmlElement {
    @Name("Ссылка сервиса")
    @FindBy(xpath = ".//a")
    public HtmlElement url;

    @Name("Имя сервиса")
    @FindBy(xpath = ".//div[contains(@class,'services-big__item_link')]")
    public HtmlElement serviceName;

    @Name("Иконка сервиса")
    @FindBy(xpath = ".//div[contains(@class,'services-big__item_icon')]")
    public HtmlElement serviceIcon;

    @Name("Комментарий к сервису")
    @FindBy(xpath = ".//div[contains(@class,'services-big__item_text')]")
    public HtmlElement description;

    public String getServiceNameAsString() {
        String result = serviceName.getText();
        return result;
    }
}
