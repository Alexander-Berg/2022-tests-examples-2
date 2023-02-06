package ru.yandex.quasar.app.rcu.observable

import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCharacteristic
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.rcu.sender.RcuCommandSender
import ru.yandex.quasar.app.rcu.sender.RcuManager
import ru.yandex.quasar.app.rcu.update.RcuInfo
import ru.yandex.quasar.app.rcu.update.RcuOtaCommands
import ru.yandex.quasar.app.rcu.update.RcuUpdateMode
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.shadows.ShadowThreadUtil

@RunWith(RobolectricTestRunner::class)
@Config(
    shadows = [ShadowThreadUtil::class],
    instrumentedPackages = ["ru.yandex.quasar.concurrency"]
)
class RcuInfoObservableTest {
    private val fakeMetricaReporter = FakeMetricaReporter()
    private val mockRcuManager: RcuManager = mock()
    private val mockCommandSender: RcuCommandSender = mock()
    private val mockBluetoothDevice: BluetoothDevice = mock()
    private val rcuConnectionObservable =
        RcuConnectionObservable(mockRcuManager, fakeMetricaReporter)

    @Before
    fun setUp() {
        whenever(mockRcuManager.getCommandSender(any())).thenReturn(mockCommandSender)
    }

    @Test
    fun when_deviceConnected_then_sendRcuInfoRequest() {
        RcuInfoObservable(mockRcuManager, RcuUpdateMode.APP, fakeMetricaReporter, rcuConnectionObservable)
        val expectedCommand = RcuOtaCommands.getRemoteAppInfoCommand

        rcuConnectionObservable.receiveValue(
            RcuConnectionObservable.RcuConnectionInfo(
                mockBluetoothDevice,
                BluetoothGatt.STATE_CONNECTED
            )
        )
        verify(mockCommandSender).send(eq(expectedCommand))
    }

    @Test
    fun when_deviceDisconnected_then_doNotSendRcuInfoRequest() {
        RcuInfoObservable(mockRcuManager, RcuUpdateMode.APP, fakeMetricaReporter, rcuConnectionObservable)
        rcuConnectionObservable.receiveValue(
            RcuConnectionObservable.RcuConnectionInfo(
                mockBluetoothDevice,
                BluetoothGatt.STATE_DISCONNECTED
            )
        )
        verify(mockCommandSender, never()).send(any())
    }

    @Test
    fun when_gotRcuInfoResponse_then_sendInfoToAll() {
        val rcuInfoObservable =
            RcuInfoObservable(mockRcuManager, RcuUpdateMode.APP, fakeMetricaReporter, rcuConnectionObservable)
        var receivedValue: Pair<BluetoothDevice, RcuInfo>? = null
        val characteristic: BluetoothGattCharacteristic = mock()
        val bytes = byteArrayOf(
            RcuOtaCommands.COMMAND_HEADER,
            RcuOtaCommands.RETURN_REMOTE_INFO,
            *ByteArray(6)
        )
        whenever(characteristic.uuid).thenReturn(RcuOtaCommands.OTA_COMMANDS_CHARACTERISTIC_UUID)
        whenever(characteristic.value).thenReturn(bytes)
        rcuInfoObservable.addObserver { receivedValue = it }

        rcuInfoObservable.onCharacteristicChanged(mockBluetoothDevice, characteristic)

        assertEquals(mockBluetoothDevice, receivedValue!!.first)
        assertEquals(0, receivedValue!!.second.imageVersion)
        assertEquals(0, receivedValue!!.second.id)
    }
}
