package ru.yandex.quasar.common.ble.main

import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothGattServer
import android.bluetooth.BluetoothManager
import android.bluetooth.le.BluetoothLeAdvertiser
import android.content.Context
import android.os.Build
import androidx.test.core.app.ApplicationProvider
import org.hamcrest.Matchers.contains
import org.hamcrest.Matchers.isEmptyString
import org.hamcrest.Matchers.not
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.shadow.api.Shadow
import org.robolectric.shadows.ShadowBluetoothAdapter
import ru.yandex.quasar.common.ble.BleNotificationSendResult
import ru.yandex.quasar.common.ble.BleServer
import ru.yandex.quasar.common.ble.CharacteristicWriteStatus
import ru.yandex.quasar.common.ble.GATT_READABLE
import ru.yandex.quasar.common.ble.GATT_WRITABLE
import ru.yandex.quasar.common.ble.GattService
import ru.yandex.quasar.common.ble.main.IsSameByteArrayMatcher.Companion.sameByteArray
import ru.yandex.quasar.common.ble.fakes.BleInitializerFake
import java.util.UUID

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.M, Build.VERSION_CODES.P])
class BleServerTest {

    private lateinit var initializer: BleInitializerFake
    private lateinit var bleServer: BleServer
    private val gattServer: BluetoothGattServer = mock()

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        Shadow.newInstanceOf(ShadowBluetoothAdapter::class.java).setEnabled(true)
        Shadow.newInstanceOf(ShadowBluetoothAdapter::class.java).setIsMultipleAdvertisementSupported(true)

        val bluetoothManager = Shadow.newInstanceOf(BluetoothManager::class.java)
        val bleAdvertiser = Shadow.newInstanceOf(BluetoothLeAdvertiser::class.java)
        initializer = BleInitializerFake(context, bluetoothManager, bleAdvertiser, gattServer)
        bleServer = BleServer(initializer, true)
    }

    fun startServer(vararg services: GattService) {
        bleServer.start(0, null, *services)
    }

    @Test
    fun when_deviceConnects_then_itIsAppendedToListOfDevices() {
        // Arrange
        startServer()
        val device: BluetoothDevice = mock()

        // Act
        initializer.gattServerCallback.onConnectionStateChange(device, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)

        // Assert
        Assert.assertEquals(1, bleServer.devices.size)
        Assert.assertThat(bleServer.devices, contains(device))
    }

    @Test
    fun when_deviceAsksForCharacteristicValue_then_itIsReadInCorrectFormat() {
        // Arrange
        val service = GattService(UUID.randomUUID())
        startServer(service)
        val characteristicUuid = UUID.randomUUID()
        val characteristic = BluetoothGattCharacteristic(characteristicUuid,
                BluetoothGattCharacteristic.PROPERTY_READ, BluetoothGattCharacteristic.PERMISSION_READ)
        service.addCharacteristic(characteristicUuid, GATT_READABLE)
        val bytes = ByteArray(10) { i -> i.toByte()}
        service.setCharacteristicValue(characteristicUuid, bytes)

        val device: BluetoothDevice = mock()
        initializer.gattServerCallback.onConnectionStateChange(device, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)

        // Act
        initializer.gattServerCallback.onCharacteristicReadRequest(device, 42, 0, characteristic)

        // Assert
        val expectedValue = byteArrayOf(1, 0, 0, 0, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        argumentCaptor<ByteArray> {
            verify(gattServer).sendResponse(eq(device),
                    eq(42),
                    eq(BluetoothGatt.GATT_SUCCESS),
                    eq(0), capture())
            Assert.assertThat(firstValue, sameByteArray(expectedValue))
        }
    }

    @Test
    fun when_deviceAsksForCharacteristicValueSeveralTimes_then_itIsReadCorrectly() {
        // Arrange
        val service = GattService(UUID.randomUUID())
        startServer(service)
        val characteristicUuid = UUID.randomUUID()
        val characteristic = BluetoothGattCharacteristic(characteristicUuid,
                BluetoothGattCharacteristic.PROPERTY_READ, BluetoothGattCharacteristic.PERMISSION_READ)
        service.addCharacteristic(characteristicUuid, GATT_READABLE)
        val bytes = ByteArray(10) { i -> i.toByte()}
        service.setCharacteristicValue(characteristicUuid, bytes)

        val device: BluetoothDevice = mock()
        initializer.gattServerCallback.onConnectionStateChange(device, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)

        // Act
        initializer.gattServerCallback.onCharacteristicReadRequest(device, 42, 0, characteristic)
        initializer.gattServerCallback.onCharacteristicReadRequest(device, 42, 0, characteristic)

        // Assert
        val expectedValue = byteArrayOf(1, 0, 0, 0, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        argumentCaptor<ByteArray> {
            verify(gattServer, times(2)).sendResponse(eq(device),
                    eq(42),
                    eq(BluetoothGatt.GATT_SUCCESS),
                    eq(0), capture())
            Assert.assertThat(firstValue, sameByteArray(expectedValue))
        }
    }

    @Test
    fun when_deviceWritesLongCharacteristicValue_then_itIsParsedCorrectly() {
        // Arrange
        val service = GattService(UUID.randomUUID())
        startServer(service)
        val characteristicUuid = UUID.randomUUID()
        val characteristic = BluetoothGattCharacteristic(characteristicUuid, 0, 0)
        service.addCharacteristic(characteristicUuid, GATT_WRITABLE)
        val bytes = byteArrayOf(1, 0, 0, 0, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

        val device: BluetoothDevice = mock()
        initializer.gattServerCallback.onConnectionStateChange(device, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)

        // Act
        initializer.gattServerCallback.onCharacteristicWriteRequest(device, 42, characteristic, false, false, 0, bytes)

        // Assert
        val actualValue = service.getCharacteristicValue(characteristicUuid)
        val expectedValue = byteArrayOf(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        Assert.assertThat(actualValue, sameByteArray(expectedValue))
    }

    @Test
    fun when_deviceWritesLongCharacteristicValueSeveralTimes_then_itIsParsedCorrectly() {
        // Arrange
        val service = GattService(UUID.randomUUID())
        startServer(service)
        val characteristicUuid = UUID.randomUUID()
        val characteristic = BluetoothGattCharacteristic(characteristicUuid, 0, 0)
        service.addCharacteristic(characteristicUuid, GATT_WRITABLE)
        val firstBytes = byteArrayOf(1, 0, 0, 0, 3, 0, 1, 2)
        val secondBytes = byteArrayOf(1, 0, 0, 0, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

        val device: BluetoothDevice = mock()
        initializer.gattServerCallback.onConnectionStateChange(device, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)

        // Act
        initializer.gattServerCallback.onCharacteristicWriteRequest(device, 42, characteristic, false, false, 0, firstBytes)
        initializer.gattServerCallback.onCharacteristicWriteRequest(device, 42, characteristic, false, false, 0, secondBytes)

        // Assert
        val actualValue = service.getCharacteristicValue(characteristicUuid)
        val expectedValue = byteArrayOf(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        Assert.assertThat(actualValue, sameByteArray(expectedValue))
    }

    @Test
    fun given_protocolVersionIsTooHigh_when_tryToWrite_writeErrorCallbackIsInvoked() {
        // Arrange
        val service = GattService(UUID.randomUUID())
        startServer(service)
        val characteristicUuid = UUID.randomUUID()
        val characteristic = BluetoothGattCharacteristic(characteristicUuid, 0, 0)
        service.addCharacteristic(characteristicUuid, GATT_WRITABLE)

        var callbackWasInvoked = false
        lateinit var status: CharacteristicWriteStatus
        bleServer.subscribeToWriteError { s ->
            callbackWasInvoked = true
            status = s
        }
        val device: BluetoothDevice = mock()

        // Act
        val bytes = byteArrayOf(99, 0, 0, 0, 3, 0, 1, 2)
        initializer.gattServerCallback.onCharacteristicWriteRequest(device, 42, characteristic,
                false, false, 0, bytes)

        // Assert
        Assert.assertTrue(callbackWasInvoked)
        Assert.assertEquals(status, CharacteristicWriteStatus.UNSUPPORTED_PROTOCOL)
    }

    fun when_notifiesAllClientsSuccessfully_then_returnsProperResult() {
        // Arrange
        val service = GattService(UUID.randomUUID())
        val characteristicUuid = UUID.randomUUID()
        service.addCharacteristic(characteristicUuid, GATT_WRITABLE)
        startServer(service)

        val device: BluetoothDevice = mock()
        whenever(device.address).thenReturn("11:11:11:11:11:11")
        initializer.gattServerCallback.onConnectionStateChange(device, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)

        // Act
        val actualResult = bleServer.notifyAllClients(characteristicUuid, byteArrayOf())

        // Assert
        val expectedResult = BleNotificationSendResult(true)
        expectedResult.addPerDeviceResult("11:11:11:11:11:11", true)
        Assert.assertEquals(expectedResult, actualResult)
    }

    @Test
    fun when_someOfClientsCantBeNotified_then_returnsProperResult() {
        // Arrange
        val service = GattService(UUID.randomUUID())
        val characteristicUuid = UUID.randomUUID()
        service.addCharacteristic(characteristicUuid, GATT_WRITABLE)
        startServer(service)

        val device1: BluetoothDevice = mock()
        whenever(device1.address).thenReturn("11:11:11:11:11:11")
        initializer.gattServerCallback.onConnectionStateChange(device1, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)
        val device2: BluetoothDevice = mock()
        whenever(device2.address).thenReturn("22:22:22:22:22:22")
        initializer.gattServerCallback.onConnectionStateChange(device2, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)
        whenever(gattServer.notifyCharacteristicChanged(eq(device2), any(), any())).thenReturn(false)

        // Act
        val actualResult = bleServer.notifyAllClients(characteristicUuid, byteArrayOf())

        // Assert
        val expectedResult = BleNotificationSendResult(true)
        expectedResult.addPerDeviceResult("11:11:11:11:11:11", true)
        expectedResult.addPerDeviceResult("22:22:22:22:22:22", false)
        Assert.assertEquals(expectedResult, actualResult)
    }

    @Test
    fun when_sendingNotificationWithNonExistingCharacteristicUuid_then_returnsProperResult() {
        // Arrange
        val service = GattService(UUID.randomUUID())
        val characteristicUuid = UUID.randomUUID()
        service.addCharacteristic(characteristicUuid, GATT_WRITABLE)
        startServer(service)

        val device: BluetoothDevice = mock()
        whenever(device.address).thenReturn("11:11:11:11:11:11")
        initializer.gattServerCallback.onConnectionStateChange(device, BluetoothGatt.GATT_SUCCESS, BluetoothGatt.STATE_CONNECTED)

        // Act
        val actualResult = bleServer.notifyAllClients(UUID.randomUUID(), byteArrayOf())

        // Assert
        Assert.assertEquals(false, actualResult.ok)
        Assert.assertThat(actualResult.err, not(isEmptyString()))
    }
}
