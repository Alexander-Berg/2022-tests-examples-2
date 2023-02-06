package com.yandex.tv.common.utility.ui.tests

import android.app.Activity
import android.util.Log
import androidx.test.platform.app.InstrumentationRegistry.getInstrumentation
import androidx.test.runner.lifecycle.ActivityLifecycleMonitorRegistry
import androidx.test.runner.lifecycle.Stage
import com.yandex.tv.common.device.utils.BoardUtils.isCvMt9632_6681
import com.yandex.tv.common.device.utils.BoardUtils.isGoya
import com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.ESPRESSO_LOG_TAG
import com.yandex.tv.common.utility.ui.tests.UiObjectHelpers.executeUiAutomationShellCommand

object SystemHelpers {

    @JvmStatic
    fun takeScreenshot(tag: String?) {
        if (isGoya() || isCvMt9632_6681()) {
            Log.d(ESPRESSO_LOG_TAG, "Skip take screenshot for goya")
        } else {
            try {
                if (tag != null) {
                    currentActivity?.let { ScreenTool.screenshot(it, tag) }
                }
            } catch (e: Exception) {
                Log.d(ESPRESSO_LOG_TAG, "Failed to take screenshot:$e")
            }
        }
    }

    @JvmStatic
    fun setBrickMode(status: Boolean) {
        val value = if (status) "1" else "0"
        executeUiAutomationShellCommand(
            "content call " +
                    "--uri content://com.yandex.tv.services.platform.brick/ " +
                    "--method put " +
                    "--arg subscription_status " +
                    "--extra value:s:$value"
        )
    }

    @JvmStatic
    val currentActivity: Activity?
        get() {
            val currentActivity = arrayOf<Activity?>(null)
            getInstrumentation().runOnMainSync {
                val resumedActivity = ActivityLifecycleMonitorRegistry.getInstance().getActivitiesInStage(Stage.RESUMED)
                val it: Iterator<Activity> = resumedActivity.iterator()
                if (it.hasNext()) {
                    currentActivity[0] = it.next()
                }
            }
            return currentActivity[0]
        }
}
