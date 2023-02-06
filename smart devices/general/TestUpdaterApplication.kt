package com.yandex.launcher.updaterapp

import android.content.Context
import com.yandex.launcher.updaterapp.common.ApplicationConfig
import com.yandex.launcher.updaterapp.core.OperationContextRegistry
import com.yandex.launcher.updaterapp.core.Server.Companion.decideUpdateServer

class TestUpdaterApplication : UpdaterApp() {

    init {
        appConfig = ApplicationConfig(
            metricaEnabled = true,
            isDatabaseMainThreadEnabled = false,
            sslEnabled = BuildConfig.SSL_ENABLED,
            useMockPackageManager = false,
            logsEnabled = BuildConfig.LOG_ENABLED,
            skipPhoneCheck = BuildConfig.SKIP_PHONE_CHECK,
            notifications = BuildConfig.NOTIFICATIONS,
            appId = BuildConfig.APPLICATION_ID,
            debugEmulateSystemInstall = BuildConfig.DEBUG_EMULATE_SYSTEM_INSTALL,
            debugAcceptAllUpdates = com.yandex.launcher.updaterapp.core.BuildConfig.DEBUG_ACCEPT_ALL_UPDATES,
            uiEnabled = BuildConfig.UI_ENABLED,
            initialServer = decideUpdateServer(BuildConfig.UPDATE_SERVER, BuildConfig.UPDATE_SERVER_FORCE_PROD),
            initialPort = BuildConfig.UPDATE_PORT,
            flavorDevice = BuildConfig.FLAVOR_device,
            autoCheckEnabled = BuildConfig.UPDATES_AUTO_CHECK_ENABLED,
            curlLogEnabled = false // curl logging breaks MockWebServer, so disable it
        )
    }

    companion object {
        fun setOperationContextRegistry(context: Context,
                                        operationContextRegistry: OperationContextRegistry) {
            UpdaterApp.setOperationContextRegistry(context, operationContextRegistry)
        }
    }
}
