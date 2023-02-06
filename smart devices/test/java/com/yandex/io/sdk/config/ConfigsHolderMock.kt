package com.yandex.io.sdk.config

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.stringPreferencesKey

class ConfigsHolderMock(
    appContext: Context,
    configServiceSdk2: YandexIoConfigServiceSdk2,
    configCache: DataStore<Preferences>
) : ConfigsHolder(appContext, configServiceSdk2, configCache) {

    val savedConfigs = mutableListOf<ConfigsContainer>()

    override val subscribedConfigs: Array<String> = arrayOf(TEST_DEFAULT_SECTION, TEST_CACHE_SECTION)

    override fun onConfig(configs: ConfigsContainer) {
        savedConfigs.add(configs)
    }

    companion object {
        const val TEST_DEFAULT_SECTION = "test_default_section"
        const val TEST_CACHE_SECTION = "test_cache_section"
    }
}
