package com.yandex.launcher.updaterapp;

import android.annotation.SuppressLint;

import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.core.configure.Configuration;
import com.yandex.launcher.updaterapp.core.configure.Configurer;

import androidx.annotation.NonNull;

@SuppressLint("Registered")
public class TestUpdaterApp extends UpdaterApp {

    private Configurer configurer;

    public TestUpdaterApp() {
        super();
        appConfig = new ApplicationConfig(false,
                true,
                false,
                true,
                false,
                false,
                BuildConfig.NOTIFICATIONS,
                BuildConfig.APPLICATION_ID,
                BuildConfig.DEBUG_EMULATE_SYSTEM_INSTALL,
                com.yandex.launcher.updaterapp.core.BuildConfig.DEBUG_ACCEPT_ALL_UPDATES,
                BuildConfig.UI_ENABLED,
                BuildConfig.UPDATE_SERVER,
                BuildConfig.UPDATE_PORT,
                BuildConfig.FLAVOR_device,
                BuildConfig.UPDATES_AUTO_CHECK_ENABLED,
                false);
    }

    public void setConfigurer(Configurer configurer) {
        this.configurer = configurer;
    }

    @NonNull
    @Override
    public Configurer getConfigurer() {
        if (configurer == null) {
            return super.getConfigurer();
        } else {
            configurer.setStoredConfiguration();
            return configurer;
        }
    }

    @NonNull
    @Override
    public Configuration getConfiguration() {
        if (configurer == null) {
            return super.getConfiguration();
        } else {
            configurer.setStoredConfiguration();
            return configurer.getCurrentConfiguration();
        }
    }
}
