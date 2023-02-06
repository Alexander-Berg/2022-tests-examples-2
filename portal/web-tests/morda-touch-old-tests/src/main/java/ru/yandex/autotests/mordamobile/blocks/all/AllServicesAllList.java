package ru.yandex.autotests.mordamobile.blocks.all;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

@Name("Центральный блок 'Все сервисы'")
@FindBy(xpath = "//div[contains(@class,'b-line__services-all')]")
public class AllServicesAllList extends HtmlElement {

    @Name("Сервис #")
    @FindBy(xpath = ".//div[contains(@class,'services-all__item_wrap')]")
    public List<HtmlElement> items;

    @Name("Рубрика #")
    @FindBy(xpath = ".//div[contains(@class,'services-all__group')]")
    public List<ServiceAllGroup> groups;

    public static class ServiceAllGroup extends HtmlElement {
        @Name("Первая буква названия сервисов")
        @FindBy(xpath = ".//div[contains(@class,'services-all__letter')]")
        public HtmlElement firstLetter;

        @Name("Список сервисов в группе")
        @FindBy(xpath = ".//div[contains(@class,'services-all__item_wrap')]")
        public List<ServiceAllItem> items;
    }

    public static class ServiceAllItem extends HtmlElement {
        @Name("Ссылка сервиса")
        @FindBy(xpath = ".//a")
        public HtmlElement href;

        @Name("Иконка сервиса")
        @FindBy(xpath = ".//div[contains(@class,'services-all__icon')]")
        public HtmlElement serviceIcon;
    }
}