package ru.yandex.autotests.mordamobile.blocks.all;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

@Name("Верхний блок с сервисами")
@FindBy(xpath = "//div[contains(@class,'b-line__services-main')]")
public class AllServicesTopList extends HtmlElement {

    @Name("Сервис #")
    @FindBy(xpath = ".//td/div[contains(@class,'services-big__wrapper')]")
    public List<ServiceTopItem> items;

    public static class ServiceTopItem extends HtmlElement {
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

        public HtmlElement getServiceName() {
            return serviceName;
        }
    }

}