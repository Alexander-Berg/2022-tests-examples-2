package ru.yandex.autotests.morda.pages.desktop.main.htmlelements;

import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.widgets.WCatalogBlock;
import ru.yandex.autotests.morda.steps.WebElementSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.matchers.common.IsElementDisplayedMatcher;

import java.util.List;

import static java.lang.Thread.sleep;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

@Name("Контролы настройки виджетного режима")
@FindBy(xpath = "//div[contains(@class, 'catalog__plate')]")
public class EditModeControls extends HtmlElement {

    @Name("Кнопка \"Вернуть\"")
    @FindBy(xpath = ".//button[contains(@class, 'catalog__undo')]")
    public HtmlElement undo;

    @Name("Кнопка \"Сбросить настройки\"")
    @FindBy(xpath = ".//button[contains(@class, 'catalog__reset')]")
    public HtmlElement reset;

    @Name("Кнопка \"Отменить\"")
    @FindBy(xpath = ".//button[contains(@class, 'catalog__revert')]")
    public HtmlElement cancel;

    @Name("Кнопка \"Сохранить\"")
    @FindBy(xpath = ".//button[contains(@class, 'catalog__save')]")
    public HtmlElement save;

    @Name("Кнопка \"Добавить новый виджет\"")
    @FindBy(xpath = ".//button[contains(@class, 'catalog__add')]")
    public HtmlElement addNewWidget;

    @Name("Каталог виджетов iframe")
    @FindBy(xpath = "//div[@class='catalog__panel']//iframe")
    public HtmlElement catalogIframe;


    @Name("Каталог виджетов")
    @FindBy(xpath = "//table[contains(@class, 'l-page')]")
    public WCatalogBlock wCatalogBlock;

    @Name("Каталог виджетов")
    @FindBy(xpath = "//a[contains(@class, 'b-catalog-widget__link')]")
    public List<HtmlElement> wCatalog;



    @Step("Добавили новый виджет")
    public void addWidget(WebDriver driver) {
        WebElementSteps.shouldSee(addNewWidget);
        WebElementSteps.clickOn(addNewWidget);
        try {
            sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println(driver.getPageSource());
        switchToIFrame(driver);
        System.out.println("============================");
//        driver.switchTo().frame(0);
        System.out.println(driver.getPageSource());
//        driver.switchTo().frame(catalogIframe);
//        System.out.println(driver.getPageSource());
//        switchDriverToEditCatalog(driver);
        try {
            sleep(5000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
//        shouldSeeSilently(wCatalogBlock);
        HtmlElement newWidget = wCatalog.stream().findFirst().get();
        System.out.println(newWidget.getText());
        newWidget.click();
    }

    @Step("Switch to widget catalog iframe")
    public void switchToIFrame(WebDriver driver){
        shouldSee(catalogIframe);
        driver.switchTo().frame(catalogIframe);
    }

    private void switchDriverToEditCatalog(WebDriver driver) {
        ((JavascriptExecutor) driver)
                .executeScript("location.href = document.getElementsByTagName('iframe')[0].src;");
    }

    @Step("Вернули удаленный виджет")
    public void undoDeletion() {
        assertThat(undo, exists());
        assertThat(undo, IsElementDisplayedMatcher.isDisplayed());
        undo.click();
    }

    @Step("Сбросили настройки виджетного режима")
    public void resetSettings() {
        assertThat(reset, exists());
        assertThat(reset, IsElementDisplayedMatcher.isDisplayed());
        reset.click();
    }

    @Step("Закрыли настройки виджетного режима")
    public void cancelSettings() {
        assertThat(cancel, exists());
        assertThat(cancel, IsElementDisplayedMatcher.isDisplayed());
        cancel.click();
    }

    @Step("Сохранили настройки виджетного режима")
    public void saveSettings() {
        assertThat(save, exists());
        assertThat(save, IsElementDisplayedMatcher.isDisplayed());
        save.click();
        try {
            sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}