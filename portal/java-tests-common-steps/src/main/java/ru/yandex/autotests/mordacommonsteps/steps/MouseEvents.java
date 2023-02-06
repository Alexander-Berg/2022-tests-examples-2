package ru.yandex.autotests.mordacommonsteps.steps;

import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.interactions.Actions;

/**
 * User: leonsabr
 * Date: 19.04.12
 */
public class MouseEvents {
    private static Actions builder;

    /**
     * Наводит курсор на элемент.
     *
     * @param driver  -- браузер
     * @param element -- элемент
     */
    public static void mouseOver(WebDriver driver, WebElement element) {
        dispatchMouseEvent(driver, "mouseover", element);
    }

    /**
     * Уводит курсор с элемента.
     *
     * @param driver  -- браузер
     * @param element -- элемент
     */
    public static void mouseOut(WebDriver driver, WebElement element) {
        dispatchMouseEvent(driver, "mouseout", element);
    }

    /**
     * Наводит курсор на элемент с помощью builder.
     *
     * @param driver  -- браузер
     * @param element -- элемент
     */
    public static void mouseTo(WebDriver driver, WebElement element) {
        builder = new Actions(driver);
        builder.moveToElement(element).perform();
    }

    private static void dispatchMouseEvent(WebDriver driver, String event, WebElement element) {
        String js = "if ( document.createEvent ) {"
                + "var eventObj = document.createEvent('MouseEvents');"
                + "eventObj.initEvent('" + event + "', false, true);"
                + "arguments[0].dispatchEvent(eventObj)"
                + "} else if ( document.createEventObject ) {"
                + "arguments[0].fireEvent('on" + event + "');"
                + "}";
        JavascriptExecutor jsExecutor = (JavascriptExecutor) driver;
        jsExecutor.executeScript(js, element);
    }
}
