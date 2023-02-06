package ru.yandex.autotests.mordacommonsteps.matchers;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.TypeSafeMatcher;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;

/**
 * User: eoff
 * Date: 11.02.13
 */
public class ModeMatcher extends TypeSafeMatcher<WebDriver> {

    public ModeMatcher(Mode mode) {
        this.mode = mode;
    }


    private Mode mode;
    private static final String BODY_XPATH = "//body";

    @Override
    protected boolean matchesSafely(WebDriver driver) {
        try {
            WebElement yamm = driver.findElement(By.xpath(BODY_XPATH));
            String attr = yamm.getAttribute(HtmlAttribute.CLASS.toString());
            return mode.getBodyMatcher().matches(attr);
        } catch (Exception e) {
            return false;
        }
    }

    @Override
    public void describeTo(Description description) {
        description.appendText(mode.getTextMatch());
    }

    @Override
    protected void describeMismatchSafely(WebDriver driver, Description mismatchDescription) {
        WebElement yamm = driver.findElement(By.xpath(BODY_XPATH));
        mismatchDescription.appendText(mode.getTextMismatch()).appendText(" url: ").appendValue(driver.getCurrentUrl());
        if (yamm == null) {
            mismatchDescription.appendText(" body not found");
        } else {
            String attr = yamm.getAttribute(HtmlAttribute.CONTENT.toString());
            if (attr == null) {
                mismatchDescription.appendText(" body has no <class>");
            } else {
                mismatchDescription.appendText(" body:").appendValue(attr);
            }
        }
    }

    @Factory
    public static ModeMatcher inPlainMode() {
        return new ModeMatcher(Mode.PLAIN);
    }

    @Factory
    public static ModeMatcher inEditMode() {
        return new ModeMatcher(Mode.EDIT);
    }

    @Factory
    public static ModeMatcher inWidgetMode() {
        return new ModeMatcher(Mode.WIDGET);
    }

    @Factory
    public static ModeMatcher inFakeMode() {
        return new ModeMatcher(Mode.FAKE);
    }
}
