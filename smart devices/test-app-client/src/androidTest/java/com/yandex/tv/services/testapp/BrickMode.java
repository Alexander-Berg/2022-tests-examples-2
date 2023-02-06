package com.yandex.tv.services.testapp;

import static com.yandex.tv.common.utility.ui.tests.SystemHelpers.setBrickMode;
import static com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.ESPRESSO_LOG_TAG;
import static com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.findUiObject2ById;
import static com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.findUiObject2ByIdWithText;
import static com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.sDevice;
import static com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.shouldNotSeeUiObject;
import static com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.shouldSeeUiObject;

import android.util.Log;
import android.view.KeyEvent;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.uiautomator.UiObject2;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

@RunWith(AndroidJUnit4.class)
public class BrickMode {

    @Before
    public void startMainActivityFromHomeScreen() {
        Log.d(ESPRESSO_LOG_TAG, "Before");

        // Start from the home screen
        sDevice.pressHome();

        // Wait for main screen
        checkMainScreenIsVisible(true);
    }

    @Test
    public void checkBrickMode() {
        Log.d(ESPRESSO_LOG_TAG, "start test");

        setBrickMode(true);

        // assert: brick mode activated
        checkBrickUiIsVisible(true);
        checkMainScreenIsVisible(false);

        // do: try to close error screen
        sDevice.pressBack();
        sDevice.pressHome();
        sDevice.pressDPadCenter();

        // assert: brick mode screen is displayed
        checkBrickUiIsVisible(true);
        checkMainScreenIsVisible(false);

        // do: try to open settings
        sDevice.pressKeyCode(KeyEvent.KEYCODE_DPAD_RIGHT);
        shouldSeeUiObject(brickOpenSettingsButton(true));
        sDevice.pressDPadCenter();

        // assert: wifi connections screen is displayed
        shouldSeeUiObject(wifiConnectTitle());

        // do: close wifi screen
        sDevice.pressBack();

        // assert: brick mode screen is displayed
        checkBrickUiIsVisible(true);
        checkMainScreenIsVisible(false);

        setBrickMode(false);

        // Wait for main screen
        checkMainScreenIsVisible(true);

        // assert: brick mode screen is displayed
        checkBrickUiIsVisible(false);

        Log.d(ESPRESSO_LOG_TAG, "stop test");
    }

    private void checkMainScreenIsVisible(boolean status) {
        if (status) {
            shouldSeeUiObject(menuItem("Поиск"));
            shouldSeeUiObject(menuItem("Главная"));
            shouldSeeUiObject(sideMenuAliceButton());
            shouldSeeUiObject(sideMenuProfileButton());
            shouldSeeUiObject(sideMenuMarketButton());
            shouldSeeUiObject(sideMenuSettingsButton());
        } else {
            shouldNotSeeUiObject(menuItem("Поиск"));
            shouldNotSeeUiObject(menuItem("Главная"));
            shouldNotSeeUiObject(sideMenuAliceButton());
            shouldNotSeeUiObject(sideMenuProfileButton());
            shouldNotSeeUiObject(sideMenuMarketButton());
            shouldNotSeeUiObject(sideMenuSettingsButton());
        }

    }

    private void checkBrickUiIsVisible(boolean status) {
        if (status) {
            shouldSeeUiObject(brickErrorPanel());
            shouldSeeUiObject(brickErrorTitle());
            shouldSeeUiObject(brickErrorMessage());
            shouldSeeUiObject(brickTryAgainButton(true));
            shouldSeeUiObject(brickOpenSettingsButton(false));
        } else {
            shouldNotSeeUiObject(brickErrorPanel());
            shouldNotSeeUiObject(brickErrorTitle());
            shouldNotSeeUiObject(brickErrorMessage());
            shouldNotSeeUiObject(brickTryAgainButton(true));
            shouldNotSeeUiObject(brickOpenSettingsButton(false));
        }

    }

    private static UiObject2 menuItem(String text) {
        return findUiObject2ByIdWithText("com.yandex.tv.home:id/header_title", text);
    }

    private static UiObject2 sideMenuAliceButton() {
        return findUiObject2ById("com.yandex.tv.home:id/alice");
    }

    private static UiObject2 sideMenuProfileButton() {
        return findUiObject2ById("com.yandex.tv.home:id/profile");
    }

    private static UiObject2 sideMenuMarketButton() {
        return findUiObject2ById("com.yandex.tv.home:id/market");
    }

    private static UiObject2 sideMenuSettingsButton() {
        return findUiObject2ById("com.yandex.tv.home:id/settings");
    }

    private static UiObject2 brickErrorPanel() {
        return findUiObject2ById("com.yandex.tv.services:id/brick_error_panel");
    }

    private static UiObject2 brickErrorTitle() {
        return findUiObject2ByIdWithText("com.yandex.tv.services:id/error_title", "Что-то пошло не так");
    }

    private static UiObject2 brickErrorMessage() {
        return findUiObject2ByIdWithText("com.yandex.tv.services:id/error_message",
                "Обновите страницу. Если ничего не изменилось, подключитесь к сети в настройках.");
    }

    public static UiObject2 brickTryAgainButton(boolean isFocused) {
        return findUiObject2ByIdWithText("com.yandex.tv.services:id/first_button", "Попробовать еще раз", isFocused);
    }

    public static UiObject2 brickOpenSettingsButton(boolean isFocused) {
        return findUiObject2ByIdWithText("com.yandex.tv.services:id/second_button", "Настроить", isFocused);
    }

    private static UiObject2 wifiConnectTitle() {
        return findUiObject2ByIdWithText("com.yandex.tv.setupwizard:id/title", "Подключитесь к Wi-Fi");
    }
}
