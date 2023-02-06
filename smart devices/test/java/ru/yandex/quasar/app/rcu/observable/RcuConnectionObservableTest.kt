package ru.yandex.quasar.app.rcu.observable

import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.mock
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.rcu.sender.RcuManager
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.shadows.ShadowThreadUtil

@RunWith(RobolectricTestRunner::class)
@Config(
    shadows = [ShadowThreadUtil::class],
    instrumentedPackages = ["ru.yandex.quasar.concurrency"]
)
class RcuConnectionObservableTest {
    private val fakeMetricaReporter = FakeMetricaReporter()
    private val mockRcuManager: RcuManager = mock()
    private val mockBluetoothDevice: BluetoothDevice = mock()

    @Test
    fun when_connectionStateChanged_then_sendStateToAll() {
        val rcuConnectionObservable = RcuConnectionObservable(mockRcuManager, fakeMetricaReporter)
        var receivedValue: RcuConnectionObservable.RcuConnectionInfo? = null
        rcuConnectionObservable.addObserver { receivedValue = it }

        rcuConnectionObservable.onConnectionStateChanged(
            mockBluetoothDevice,
            BluetoothGatt.STATE_CONNECTED
        )

        assertEquals(mockBluetoothDevice, receivedValue!!.device)
        assertEquals(BluetoothGatt.STATE_CONNECTED, receivedValue!!.connectionState)
    }

    @Test
    fun when_connectionStateChanged_then_sendReportToMetrica() {
        val rcuConnectionObservable = RcuConnectionObservable(mockRcuManager, fakeMetricaReporter)

        rcuConnectionObservable.onConnectionStateChanged(
            mockBluetoothDevice,
            BluetoothGatt.STATE_DISCONNECTED
        )

        assertEquals(1, fakeMetricaReporter.events.size)
        val event = fakeMetricaReporter.events.first()
        assertEquals("RcuDeviceDisconnected", event.name)
        assertEquals(mapOf("name" to null, "address" to null), event.mapData1)
    }
}
