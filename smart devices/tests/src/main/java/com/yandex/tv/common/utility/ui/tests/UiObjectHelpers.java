package com.yandex.tv.common.utility.ui.tests;

import static androidx.test.platform.app.InstrumentationRegistry.getInstrumentation;
import static com.yandex.tv.common.utility.ui.tests.EspressoIdling.sleepStatement;
import static junit.framework.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.fail;
import static java.lang.String.format;

import android.content.Context;
import android.util.Log;

import androidx.test.uiautomator.By;
import androidx.test.uiautomator.BySelector;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.UiObject;
import androidx.test.uiautomator.UiObject2;
import androidx.test.uiautomator.UiSelector;
import androidx.test.uiautomator.Until;

import junit.framework.AssertionFailedError;

import java.io.IOException;
import java.util.regex.Pattern;

public class UiObjectHelpers {

    public static UiDevice sDevice = UiDevice.getInstance(getInstrumentation());
    public static Context sTargetContext = getInstrumentation().getTargetContext();
    public static String sTargetPackage = sTargetContext.getPackageName();
    private static final int TIMEOUT_FOR_OTHER_APP_LAUNCHED = 50000;
    public static final int TIMEOUT_WAIT_FOR_ITEMS = 8000; //ms
    public static final int DEFAULT_TIMEOUT_BETWEEN_ACTIONS = 3000; //ms
    public static final String ESPRESSO_LOG_TAG = "ESPRESSO_TEST";

    /**
     * UiObject methods
     **/

    public static UiObject findUiObjectById(String id) {
        return sDevice.findObject(new UiSelector().resourceId(id));
    }

    public static UiObject findUiObjectById(int id) {
        return sDevice.findObject(new UiSelector().resourceId(sTargetContext.getResources().getResourceName(id)));
    }

    public static UiObject findUiObjectByIdWithText(String Id, String text) {
        return sDevice.findObject(new UiSelector().resourceId(Id).text(text));
    }

    public static UiObject findUiObjectByIdWithText(int resId, String text) {
        return sDevice.findObject(new UiSelector().resourceId(sTargetContext.getResources().getResourceName(resId))
                .text(text));
    }

    public static UiObject findUiObjectByIdWithTextContains(int resId, String text) {
        return sDevice.findObject(new UiSelector().resourceId(sTargetContext.getResources().getResourceName(resId))
                .textContains(text));
    }

    public static UiObject findUiObjectByText(String text) {
        return sDevice.findObject(new UiSelector().text(text));
    }

    public static UiObject findUiObjectByText(int stringId) {
        return sDevice.findObject(new UiSelector().text(sTargetContext.getString(stringId)));
    }

    public static UiObject findUiObjectByTextContains(String text) {
        return sDevice.findObject(new UiSelector().textContains(text));
    }

    public static UiObject findUiObjectByTextContains(int stringId) {
        return sDevice.findObject(new UiSelector().textContains(sTargetContext.getString(stringId)));
    }

    public static UiObject findUiObjectByDesc(String text) {
        return sDevice.findObject(new UiSelector().description(text));
    }

    public static UiObject findUiObjectByDesc(int stringId) {
        return sDevice.findObject(new UiSelector().description(sTargetContext.getString(stringId)));
    }

    public static UiObject findUiObjectByDescContains(String text) {
        return sDevice.findObject(new UiSelector().descriptionContains(text));
    }

    public static UiObject findUiObjectByDescContains(int stringId) {
        return sDevice.findObject(new UiSelector().descriptionContains(sTargetContext.getString(stringId)));
    }

    public static UiObject findUiObjectByIdWithPosition(String className, int resId, int position) {
        return sDevice.findObject(new UiSelector()
                .className(className)
                .index(position)
                .fromParent(new UiSelector().resourceId(sTargetContext.getResources().getResourceName(resId))));
    }

    public static UiObject uiObjectWithIdIsScrollable(int stringId) {
        return sDevice.findObject(new UiSelector().text(sTargetContext.getString(stringId))
                .scrollable(true));
    }

    public static UiObject findPackageByUiObject(String name) {
        return sDevice.findObject(new UiSelector().packageName(name));
    }

    public static UiObject findUiObjectByClassName(String className) {
        return sDevice.findObject(new UiSelector().className(className));
    }

    /**
     * UiObject2 methods
     **/

    public static UiObject2 findUiObject2ById(String Id) {
        return sDevice.wait(Until.findObject(By.res(Id)),
                TIMEOUT_WAIT_FOR_ITEMS);
    }

    public static UiObject2 findUiObject2ById(String Id, int timeout) {
        return sDevice.wait(Until.findObject(By.res(Id)),
                timeout);
    }

    public static UiObject2 findUiObject2ById(String Id, boolean isChecked) {
        return sDevice.wait(Until.findObject(By.res(Id).checked(isChecked)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ById(int resId) {
        return sDevice.wait(Until.findObject(getSelectorForId(resId)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByIdWithText(int resId, int text, int timeout) {
        return sDevice.wait(Until.findObject(getSelectorForId(resId).text(sTargetContext.getString(text))),
                timeout);
    }

    public static UiObject2 findUiObject2ByIdWithText(String Id, String text) {
        return sDevice.wait(Until.findObject(By.res(Id).text(text)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByIdWithText(String Id, String text, int timeout) {
        return sDevice.wait(Until.findObject(By.res(Id).text(text)),
                timeout);
    }

    public static UiObject2 findUiObject2ByIdWithText(String Id, String text, boolean isFocused) {
        return sDevice.wait(Until.findObject(By.res(Id).text(text).focused(isFocused)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByIdWithText(String Id, String text, boolean isFocused, int timeout) {
        return sDevice.wait(Until.findObject(By.res(Id).text(text).focused(isFocused)),
                timeout);
    }

    public static UiObject2 findUiObject2ByPackageWithText(String idPackage, String text) {
        return sDevice.wait(Until.findObject(By.pkg(idPackage).text(text)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByPackageWithDesc(String idPackage, String desc) {
        return sDevice.wait(Until.findObject(By.pkg(idPackage).desc(desc)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByIdWithTextContains(String Id, String text) {
        return sDevice.wait(Until.findObject(By.res(Id).textContains(text)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByIdWithTextContains(int resId, String text) {
        String name = sTargetContext.getResources().getResourceEntryName(resId);
        return sDevice.wait(Until.findObject(By.res(sTargetPackage, name).textContains(text)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByText(String text) {
        return sDevice.wait(Until.findObject(By.text(text)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByText(String text, int timeout) {
        return sDevice.wait(Until.findObject(By.text(text)), timeout);
    }

    public static UiObject2 findUiObject2ByText(int stringId) {
        return sDevice.wait(Until.findObject(By.text(sTargetContext.getString(stringId))),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByTextPattern(Pattern pattern) {
        return sDevice.wait(Until.findObject(By.text(pattern)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByTextContains(String text) {
        return sDevice.wait(Until.findObject(By.textContains(text)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByTextContains(int stringId) {
        return sDevice.wait(Until.findObject(By.textContains(sTargetContext.getString(stringId))),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByDesc(String desc) {
        return sDevice.wait(Until.findObject(By.desc(desc)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByDesc(int stringId) {
        return sDevice.wait(Until.findObject(By.desc(sTargetContext.getString(stringId))),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByDescContains(String desc) {
        return sDevice.wait(Until.findObject(By.descContains(desc)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByDescContains(int stringId) {
        return sDevice.wait(Until.findObject(By.descContains(sTargetContext.getString(stringId))),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByClassName(String className) {
        return sDevice.wait(Until.findObject(By.clazz(className)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findPackageNameByUiObject2(String packageName) {
        return sDevice.wait(Until.findObject(By.pkg(packageName)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    public static UiObject2 findUiObject2ByIdWithText(int resId, String text) {
        String name = sTargetContext.getResources().getResourceEntryName(resId);
        return sDevice.wait(Until.findObject(By.res(sTargetPackage, name).text(text)),
                DEFAULT_TIMEOUT_BETWEEN_ACTIONS);
    }

    /**
     * Selectors for UiObject2 methods
     **/

    public static BySelector getSelectorForId(int resId) {
        String name = sTargetContext.getResources().getResourceEntryName(resId);
        return By.res(sTargetPackage, name);
    }

    public static void shouldSeeUiObject(UiObject... ob) {
        for (UiObject item : ob) {
            try {
                assertNotNull(item);
            } catch (AssertionFailedError e) {
                fail("UiObject is not found!");
            }
        }
    }

    public static void shouldSeeUiObject(UiObject2... ob) {
        for (UiObject2 item : ob) {
            try {
                assertNotNull(item);
            } catch (AssertionError e) {
                fail("UiObject is not found!");
            }
        }
    }

    public static void shouldNotSeeUiObject(UiObject2... ob) {
        for (UiObject2 item : ob) {
            try {
                assertNull(item);
            } catch (AssertionError e) {
                fail(format("UiObject %s is found!", item.getResourceName()));
            }
        }
    }

    public static void shouldSeeUiFromOtherApp(UiObject object) {
        if (!object.waitForExists(TIMEOUT_FOR_OTHER_APP_LAUNCHED)) {
            fail(object + " is not found!");
        }
    }

    public static void checkLaunchedApp(AppsInfo packageName) {
        UiObject pkgName = findPackageByUiObject(packageName.getPackageName());
        if (!pkgName.waitForExists(TIMEOUT_FOR_OTHER_APP_LAUNCHED)) {
            fail(packageName + " is not found!");
        }
    }

    public static void clearStorageOfApp(String packageName) {
        executeUiAutomationShellCommand("pm clear " + packageName);
    }

    public static void forceStopApp(String packageName) {
        executeUiAutomationShellCommand("am force-stop " + packageName);
    }

    public static void executeUiAutomationShellCommand(String shellCommand) {
        try {
            Log.d(ESPRESSO_LOG_TAG, "executeUiAutomationShellCommand " + shellCommand);
            UiObjectHelpers.sDevice.executeShellCommand(shellCommand);
            sleepStatement(TIMEOUT_WAIT_FOR_ITEMS);
        } catch (IOException e) {
            fail(format("Failed execute shell command: %s", shellCommand));
        }
    }

    public static void executeSendEventShellCommand(String sendevent) {
        try {
            Log.d(ESPRESSO_LOG_TAG, "executeSendEventShellCommand " + sendevent);
            UiObjectHelpers.sDevice.executeShellCommand(sendevent);
        } catch (IOException e) {
            fail(format("Failed execute shell command: %s", sendevent));
        }
    }

    public static String executeShellCommand(String shellCommand) {
        String result = null;
        try {
            Log.d(ESPRESSO_LOG_TAG, "executeShellCommand " + shellCommand);
            result = UiObjectHelpers.sDevice.executeShellCommand(shellCommand);
            sleepStatement(TIMEOUT_WAIT_FOR_ITEMS);
        } catch (IOException e) {
            fail(format("Failed execute shell command: %s", shellCommand));
        }
        Log.d(ESPRESSO_LOG_TAG, "executeShellCommand result - " + result);
        return result;
    }

    public static boolean isUiObject2IsVisible(UiObject2 object) {
        try {
            assertNotNull(object);
            return true;
        } catch (AssertionError e) {
            return false;
        }
    }
}
