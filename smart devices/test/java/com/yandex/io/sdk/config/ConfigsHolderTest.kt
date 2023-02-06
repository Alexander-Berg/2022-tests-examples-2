package com.yandex.io.sdk.config

import android.app.Application
import android.content.Context
import android.content.res.AssetManager
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import androidx.test.core.app.ApplicationProvider
import com.yandex.io.sdk.config.ConfigsHolderMock.Companion.TEST_CACHE_SECTION
import com.yandex.io.sdk.config.ConfigsHolderMock.Companion.TEST_DEFAULT_SECTION
import com.yandex.io.sdk.proto.BackendConfigProto
import com.yandex.tv.services.common.internal.AbstractServiceRemoteSdk
import com.yandex.tv.services.common.internal.CompletableServiceFuture
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers
import org.junit.After
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.doThrow
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.spy
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import java.io.IOException

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(RobolectricTestRunner::class)
class ConfigsHolderTest {

    private val context = spy(ApplicationProvider.getApplicationContext<Application>())
    private val assets: AssetManager = mock()
    private val ioSdk = mock<AbstractServiceRemoteSdk<IYandexIoConfigService>>(extraInterfaces = arrayOf(YandexIoConfigServiceSdk2::class)) as YandexIoConfigServiceSdk2
    private val Context.dataStore by preferencesDataStore("test")

    private val holder by lazy {
        ConfigsHolderMock(context, ioSdk, context.dataStore)
    }

    @Before
    fun setUp() {
        val completedFuture = CompletableServiceFuture<Void>().apply { complete(null) }
        whenever(ioSdk.subscribeToConfig(any(), any(), any())).doReturn(completedFuture)
        whenever(context.assets).doReturn(assets)
    }

    @After
    fun clear() = runTest {
        context.dataStore.edit {
            it.clear()
        }
    }

    @Test
    fun `initialize() not set default config if empty`() {
        whenever(assets.open(eq(DEFAULT_SYSTEM_CONFIG_ASSET))).doReturn("{}".byteInputStream())

        holder.initialize()

        assertThat(holder.savedConfigs, Matchers.empty())
    }

    @Test
    fun `initialize() not set default config if no asset`() {
        whenever(assets.open(eq(DEFAULT_SYSTEM_CONFIG_ASSET))).doThrow(IOException("no asset"))

        holder.initialize()

        assertThat(holder.savedConfigs, Matchers.empty())
    }

    @Test
    fun `initialize() set default config from assets`() {
        whenever(assets.open(eq(DEFAULT_SYSTEM_CONFIG_ASSET))).doReturn(ASSET_DEFAULT_CONFIG.byteInputStream())

        holder.initialize()

        val expected = mapOf(TEST_DEFAULT_SECTION to DEFAULT_CONFIG_VALUE)
        assertThat(holder.savedConfigs, Matchers.hasSize(1))
        assertThat(holder.savedConfigs.first().configs, Matchers.equalTo(expected))
    }

    @Test
    fun `initialize() set cached config`() = runTest {
        whenever(assets.open(eq(DEFAULT_SYSTEM_CONFIG_ASSET))).doReturn("{}".byteInputStream())
        context.dataStore.edit { preferences ->
            preferences[stringPreferencesKey(TEST_CACHE_SECTION)] = CACHE_CONFIG_VALUE
        }

        holder.initialize()

        val expected = mapOf(TEST_CACHE_SECTION to CACHE_CONFIG_VALUE)
        assertThat(holder.savedConfigs, Matchers.hasSize(1))
        assertThat(holder.savedConfigs.first().configs, Matchers.equalTo(expected))
    }

    @Test
    fun `initialize() set cached and default configs`() = runTest {
        whenever(assets.open(eq(DEFAULT_SYSTEM_CONFIG_ASSET))).doReturn(ASSET_DEFAULT_CONFIGS.byteInputStream())
        context.dataStore.edit { preferences ->
            preferences[stringPreferencesKey(TEST_CACHE_SECTION)] = CACHE_CONFIG_VALUE
        }

        holder.initialize()

        val expected = mapOf(TEST_CACHE_SECTION to CACHE_CONFIG_VALUE, TEST_DEFAULT_SECTION to DEFAULT_CONFIG_VALUE)
        assertThat(holder.savedConfigs, Matchers.hasSize(1))
        assertThat(holder.savedConfigs.first().configs, Matchers.equalTo(expected))
    }

    @Test
    fun `config receiving put it to cache and onSystemConfig()`() = runTest {
        val config = BackendConfigProto.BackendConfig.newBuilder().setName(TEST_CACHE_SECTION).setValue(CACHE_CONFIG_VALUE).build()
        whenever(ioSdk.subscribeToConfig(any(), any(), any())).then {
            (it.arguments[0] as ConfigSdkClientBinder).onIncomingMessage(config, mock())
            CompletableServiceFuture<Void?>().apply { complete(null) }
        }

        holder.initialize()

        val expected = mapOf(TEST_CACHE_SECTION to CACHE_CONFIG_VALUE)
        val cache = context.dataStore.data.first()
        for (el in expected) {
            assertThat(cache[stringPreferencesKey(el.key)], Matchers.equalTo(el.value))
        }
        assertThat(holder.savedConfigs, Matchers.hasSize(1))
        assertThat(holder.savedConfigs.first().configs, Matchers.equalTo(expected))
    }

    @Test
    fun `default config doesn't append new keys to received one`() = runTest {
        whenever(assets.open(eq(DEFAULT_SYSTEM_CONFIG_ASSET))).doReturn(ASSET_DEFAULT_CONFIGS.byteInputStream())
        val configTestSection = BackendConfigProto.BackendConfig.newBuilder().setName(TEST_CACHE_SECTION).setValue(RICH_CONFIG_VALUE).build()
        val configDefaultSection = BackendConfigProto.BackendConfig.newBuilder().setName(TEST_DEFAULT_SECTION).setValue(DEFAULT_CONFIG_VALUE).build()
        whenever(ioSdk.subscribeToConfig(any(), eq(ConfigsContainer.ofNames(arrayOf(TEST_CACHE_SECTION))), any())).then {
            (it.arguments[0] as ConfigSdkClientBinder).onIncomingMessage(configTestSection, mock())
            CompletableServiceFuture<Void?>().apply { complete(null) }
        }
        whenever(ioSdk.subscribeToConfig(any(), eq(ConfigsContainer.ofNames(arrayOf(TEST_DEFAULT_SECTION))), any())).then {
            (it.arguments[0] as ConfigSdkClientBinder).onIncomingMessage(configDefaultSection, mock())
            CompletableServiceFuture<Void?>().apply { complete(null) }
        }

        holder.initialize()

        holder.savedConfigs.stream().skip(1).forEach {
            // Every config (except for init defualt config) should contain both values from RICH_CONFIG_VALUE or none.
            // Config with default values only are prohibited
            if (it.configs.containsKey(TEST_CACHE_SECTION)) {
                assertThat(it.configs.keys, Matchers.contains("test_key"))
                assertThat(it.configs.keys, Matchers.contains("test_key2"))
            }
        }
    }

    private companion object {
        const val DEFAULT_SYSTEM_CONFIG_ASSET = "tv_config.json"

        const val DEFAULT_CONFIG_VALUE = "{\"test_key\":123}"
        const val CACHE_CONFIG_VALUE = "{\"test_key\":234}"
        const val RICH_CONFIG_VALUE = "{\"test_key\":234,\"test_key2\":9}"
        const val ASSET_DEFAULT_CONFIG = "{\"$TEST_DEFAULT_SECTION\":$DEFAULT_CONFIG_VALUE}"
        const val ASSET_DEFAULT_CONFIGS = "{\"$TEST_DEFAULT_SECTION\":$DEFAULT_CONFIG_VALUE,\"$TEST_CACHE_SECTION\":$DEFAULT_CONFIG_VALUE}"
    }
}
