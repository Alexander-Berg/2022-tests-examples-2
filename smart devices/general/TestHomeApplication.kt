package com.yandex.tv.home.utils

import com.yandex.tv.common.config.di.DeviceComponent
import com.yandex.tv.home.HomeApplication

class TestHomeApplication : HomeApplication() {

    private var firstRunPref = "first_run"
    private var homeAppPrefsFileName = "com.yandex.tv.home_preferences"

    override fun onCreate() {
        changePreferencesForTests()
        super.onCreate()
        // for fix kotlin.UninitializedPropertyAccessException: lateinit property instance has not been initialized
        DeviceComponent.instance = DeviceComponent()
    }

    private fun changePreferencesForTests() {
        val preferences = applicationContext.getSharedPreferences(homeAppPrefsFileName, MODE_PRIVATE)
        val editor = preferences.edit()

        // Android test orchestrator deletes SharedPreferences before the test, so the "recent" carousel is missing during the test.
        // To fix this we change boolean "first_run" to true and the "recent" carousel is created again.
        editor.putBoolean(firstRunPref, true)
        editor.commit()
    }
}
