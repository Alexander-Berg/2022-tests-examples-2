package com.yandex.io.sdk.environment

import android.app.Application
import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.yandex.io.sdk.config.YandexIoConfigsHolder
import com.yandex.io.sdk.contract.EnvironmentProviderContract
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.nullValue
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Assert.assertThrows
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.protobuf.ModelObjects.DeviceGroupState

@RunWith(RobolectricTestRunner::class)
class EnvironmentContentProviderTest {
    @Test
    fun `no permissions, call getTandemInfo, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        val glagolContentProvider = createGlagolContentProvider(context)

        assertThrows(SecurityException::class.java) {
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_TANDEM_INFO, null, null)
        }
    }

    @Test
    fun `no permissions, call isInTandem, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        val glagolContentProvider = createGlagolContentProvider(context)

        assertThrows(SecurityException::class.java) {
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_IS_IN_TANDEM, null, null)
        }
    }

    @Test
    fun `no permissions, call getGlagolDiscovery, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        val glagolContentProvider = createGlagolContentProvider(context)

        assertThrows(SecurityException::class.java) {
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_GLAGOL_DISCOVERY, null, null)
        }
    }

    @Test
    fun `no permissions, call getTandemDiscovery, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        val glagolContentProvider = createGlagolContentProvider(context)

        assertThrows(SecurityException::class.java) {
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_TANDEM_DISCOVERY, null, null)
        }
    }

    @Test
    fun `no permissions, call isDiscoveredDevicesAvailableToTandem, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        val glagolContentProvider = createGlagolContentProvider(context)

        assertThrows(SecurityException::class.java) {
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_IS_DISCOVERED_DEVICES_AVAILABLE_TO_TANDEM, null, null)
        }
    }

    @Test
    fun `no permissions, call isTandemSettingsEnabled, throw SecurityException`() {
        val context = getAppContextWithoutPermissions()
        val glagolContentProvider = createGlagolContentProvider(context)

        assertThrows(SecurityException::class.java) {
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_IS_TANDEM_SETTINGS_ENABLED, null, null)
        }
    }

    @Test
    fun `have permission, call getTandemInfo, no exception`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_TANDEM_INFO, null, null)
    }

    @Test
    fun `have permission, call isInTandem, no exception`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        glagolContentProvider.call(EnvironmentProviderContract.METHOD_IS_IN_TANDEM, null, null)
    }

    @Test
    fun `have permission, call getGlagolDiscovery, no exception`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_GLAGOL_DISCOVERY, null, null)
    }

    @Test
    fun `have permission, call getTandemDiscovery, no exception`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_TANDEM_DISCOVERY, null, null)
    }

    @Test
    fun `have permission, call isDiscoveredDevicesAvailableToTandem, no exception`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        glagolContentProvider.call(EnvironmentProviderContract.METHOD_IS_DISCOVERED_DEVICES_AVAILABLE_TO_TANDEM, null, null)
    }

    @Test
    fun `have permission, call isTandemSettingsEnabled, no exception`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        glagolContentProvider.call(EnvironmentProviderContract.METHOD_IS_TANDEM_SETTINGS_ENABLED, null, null)
    }

    @Test
    fun `received tandem info, call getTandemInfo, return tandem info`() {
        val context = getAppContext()
        val glagolContentProviderImpl = createGlagolContentProviderImpl(context)

        val leaderPlatform = "some_platform"
        val leaderId = "some_id"
        val deviceGroupState = DeviceGroupState.newBuilder()
            .setLocalRole(DeviceGroupState.Role.FOLLOWER)
            .setGroupId(42)
            .setLeader(
                DeviceGroupState.Leader.newBuilder()
                    .setConnectionState(DeviceGroupState.ConnectionState.CONNECTED)
                    .setPlatform(leaderPlatform)
                    .setDeviceId(leaderId)
            )
            .build()
        glagolContentProviderImpl.onDeviceGroupState(deviceGroupState)

        val expectedTandemInfo = TandemInfo(
            42,
            TandemRole.FOLLOWER,
            TandemPairedDevice(TandemPairedDevice.ConnectionState.CONNECTED, leaderPlatform, leaderId)
        )

        val bundle =
            glagolContentProviderImpl.call(EnvironmentProviderContract.METHOD_GET_TANDEM_INFO, null, null)
        val actualTandemInfo = TandemInfo.Factory.fromBundle(bundle)
        assertThat(actualTandemInfo, equalTo(expectedTandemInfo))
    }

    @Test
    fun `received tandem info, call isInTandem, return true`() {
        val context = getAppContext()
        val glagolContentProviderImpl = createGlagolContentProviderImpl(context)

        val leaderPlatform = "some_platform"
        val leaderId = "some_id"
        val deviceGroupState = DeviceGroupState.newBuilder()
            .setLocalRole(DeviceGroupState.Role.FOLLOWER)
            .setLeader(
                DeviceGroupState.Leader.newBuilder()
                    .setConnectionState(DeviceGroupState.ConnectionState.CONNECTED)
                    .setPlatform(leaderPlatform)
                    .setDeviceId(leaderId)
            )
            .build()
        glagolContentProviderImpl.onDeviceGroupState(deviceGroupState)

        val bundle =
            glagolContentProviderImpl.call(EnvironmentProviderContract.METHOD_IS_IN_TANDEM, null, null)
        val isInTandem = bundle?.getBoolean(EnvironmentProviderContract.RESULT_IS_IN_TANDEM)
        assertThat(isInTandem, equalTo(true))
    }

    @Test
    fun `received glagol discovery info, call getGlagolDiscovery, return discovery result`() {
        val context = getAppContext()
        val glagolContentProviderImpl = createGlagolContentProviderImpl(context)

        val discoveryItems = getAllDiscoveryItems()
        val discoveryResult = ModelObjects.GlagolDiscoveryResult.newBuilder().addAllItems(discoveryItems).build()
        glagolContentProviderImpl.onDiscoveryResult(discoveryResult)

        val expectedDiscoveryResult = GlagolDiscoveryResult.Factory.fromProto(discoveryResult)

        val bundle =
            glagolContentProviderImpl.call(EnvironmentProviderContract.METHOD_GET_GLAGOL_DISCOVERY, null, null)
        val actualDiscoveryResult = GlagolDiscoveryResult.fromBundle(bundle)
        assertThat(actualDiscoveryResult, equalTo(expectedDiscoveryResult))
    }

    @Test
    fun `received glagol discovery info, call getTandemDiscovery, return only tandem available`() {
        val context = getAppContext()
        val glagolContentProviderImpl = createGlagolContentProviderImpl(context)

        val availableToTandemItems = getAvailableToTandemItems()
        val allDiscoveryItems = getAllDiscoveryItems()

        glagolContentProviderImpl.onDiscoveryResult(
            ModelObjects.GlagolDiscoveryResult.newBuilder().addAllItems(allDiscoveryItems).build()
        )

        val expectedDiscoveryResult = GlagolDiscoveryResult.Factory.fromProto(
            ModelObjects.GlagolDiscoveryResult.newBuilder().addAllItems(availableToTandemItems).build()
        )

        val bundle =
            glagolContentProviderImpl.call(EnvironmentProviderContract.METHOD_GET_TANDEM_DISCOVERY, null, null)
        val actualTandemDiscoveryResult = GlagolDiscoveryResult.fromBundle(bundle)
        assertThat(actualTandemDiscoveryResult, equalTo(expectedDiscoveryResult))
    }

    @Test
    fun `received glagol discovery info with unavailable to tandem items, call isDiscoveredDevicesAvailableToTandem, return false`() {
        val context = getAppContext()
        val glagolContentProviderImpl = createGlagolContentProviderImpl(context)

        val discoveryItems = getUnavailableToTandemItems()
        glagolContentProviderImpl.onDiscoveryResult(
            ModelObjects.GlagolDiscoveryResult.newBuilder().addAllItems(discoveryItems).build()
        )

        val bundle =
            glagolContentProviderImpl.call(EnvironmentProviderContract.METHOD_IS_DISCOVERED_DEVICES_AVAILABLE_TO_TANDEM, null, null)
        val isAvailable = bundle?.getBoolean(EnvironmentProviderContract.RESULT_IS_DISCOVERED_DEVICES_AVAILABLE_TO_TANDEM)
        assertThat(isAvailable, equalTo(false))
    }

    @Test
    fun `received glagol discovery info with available to tandem items, call isDiscoveredDevicesAvailableToTandem, return true`() {
        val context = getAppContext()
        val glagolContentProviderImpl = createGlagolContentProviderImpl(context)

        val discoveryItems = getAllDiscoveryItems()
        glagolContentProviderImpl.onDiscoveryResult(
            ModelObjects.GlagolDiscoveryResult.newBuilder().addAllItems(discoveryItems).build()
        )

        val bundle =
            glagolContentProviderImpl.call(EnvironmentProviderContract.METHOD_IS_DISCOVERED_DEVICES_AVAILABLE_TO_TANDEM, null, null)
        val isAvailable = bundle?.getBoolean(EnvironmentProviderContract.RESULT_IS_DISCOVERED_DEVICES_AVAILABLE_TO_TANDEM)
        assertThat(isAvailable, equalTo(true))
    }

    @Test
    fun `no tandem info received, call getTandemInfo, return null`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        val bundle =
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_TANDEM_INFO, null, null)
        val actualTandemInfo = TandemInfo.Factory.fromBundle(bundle)

        assertThat(actualTandemInfo, nullValue())
    }

    @Test
    fun `no tandem info received, call isInTandme, return false`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        val bundle =
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_IS_IN_TANDEM, null, null)
        val isInTandem = bundle?.getBoolean(EnvironmentProviderContract.RESULT_IS_IN_TANDEM)

        assertThat(isInTandem, equalTo(false))
    }

    @Test
    fun `no glagol discovery info received, call getGlagolDiscovery, return null`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        val bundle =
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_GLAGOL_DISCOVERY, null, null)

        assertThat(bundle, nullValue())
    }

    @Test
    fun `no glagol discovery info received, call getTandemDiscovery, return null`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        val bundle =
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_GET_TANDEM_DISCOVERY, null, null)

        assertThat(bundle, nullValue())
    }

    @Test
    fun `no glagol discovery info received, call isDiscoveredDevicesAvailableToTandem, return false`() {
        val context = getAppContext()
        val glagolContentProvider = createGlagolContentProvider(context)

        val bundle =
            glagolContentProvider.call(EnvironmentProviderContract.METHOD_IS_DISCOVERED_DEVICES_AVAILABLE_TO_TANDEM, null, null)
        val isAvailable = bundle?.getBoolean(EnvironmentProviderContract.RESULT_IS_DISCOVERED_DEVICES_AVAILABLE_TO_TANDEM)

        assertThat(isAvailable, equalTo(false))
    }

    private fun createGlagolContentProvider(context: Context): EnvironmentContentProvider {
        return EnvironmentContentProvider().apply { lateInit(createGlagolContentProviderImpl(context)) }
    }

    private fun createGlagolContentProviderImpl(context: Context): EnvironmentContentProviderImpl {
        return EnvironmentContentProviderImpl(
            context,
            YandexIoConfigsHolder(ApplicationProvider.getApplicationContext()))
    }

    private fun getAllDiscoveryItems(): List<ModelObjects.GlagolDiscoveryItem> {
        return mutableListOf<ModelObjects.GlagolDiscoveryItem>().apply {
            addAll(getAvailableToTandemItems())
            addAll(getUnavailableToTandemItems())
        }
    }

    private fun getAvailableToTandemItems(): List<ModelObjects.GlagolDiscoveryItem> {
        val discoveryList = mutableListOf<ModelObjects.GlagolDiscoveryItem>()
        for (i in 1..3) {
            discoveryList.add(
                ModelObjects.GlagolDiscoveryItem
                    .newBuilder()
                    .setIsAccountDevice(true)
                    .setDeviceId("deviceId$i")
                    .setPlatform("yandexstation_2").build()
            )
        }
        return discoveryList
    }

    private fun getUnavailableToTandemItems(): List<ModelObjects.GlagolDiscoveryItem> {
        return listOf(
            ModelObjects.GlagolDiscoveryItem.newBuilder()
                .setIsAccountDevice(false)
                .build(),
            ModelObjects.GlagolDiscoveryItem.newBuilder()
                .setIsAccountDevice(true)
                .setDeviceId("")
                .build(),
            ModelObjects.GlagolDiscoveryItem.newBuilder()
                .setIsAccountDevice(true)
                .setDeviceId("some_id")
                .setPlatform("unsupported_platform")
                .build()
        )
    }

    private fun getAppContext(): Context {
        val context = ApplicationProvider.getApplicationContext<Application>()
        val shadowApp = Shadows.shadowOf(context)
        shadowApp.grantPermissions(EnvironmentProviderContract.PERMISSION_READ_ENVIRONMENT_INFO)
        return context
    }

    private fun getAppContextWithoutPermissions(): Context {
        return ApplicationProvider.getApplicationContext<Application>()
    }
}
