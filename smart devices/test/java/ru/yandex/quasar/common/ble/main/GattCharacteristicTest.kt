package ru.yandex.quasar.common.ble.main

import android.bluetooth.BluetoothGattCharacteristic
import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.common.ble.GATT_NOTIFY
import ru.yandex.quasar.common.ble.GATT_READABLE
import ru.yandex.quasar.common.ble.GATT_WRITABLE
import ru.yandex.quasar.common.ble.getPermission
import ru.yandex.quasar.common.ble.getProperty


@RunWith(RobolectricTestRunner::class)
class GattCharacteristicTest {
    @Test
    fun characteristicPermissionsAndPropertiesAreCalculatedCorrectly() {
        Assert.assertEquals(BluetoothGattCharacteristic.PROPERTY_READ, GATT_READABLE.getProperty())
        Assert.assertEquals(BluetoothGattCharacteristic.PERMISSION_READ, GATT_READABLE.getPermission())

        Assert.assertEquals(BluetoothGattCharacteristic.PROPERTY_WRITE, GATT_WRITABLE.getProperty())
        Assert.assertEquals(BluetoothGattCharacteristic.PERMISSION_WRITE, GATT_WRITABLE.getPermission())

        Assert.assertEquals(BluetoothGattCharacteristic.PROPERTY_READ or BluetoothGattCharacteristic.PROPERTY_WRITE,
                (GATT_READABLE or GATT_WRITABLE).getProperty())
        Assert.assertEquals(BluetoothGattCharacteristic.PERMISSION_READ or BluetoothGattCharacteristic.PERMISSION_WRITE,
                (GATT_READABLE or GATT_WRITABLE).getPermission())

        Assert.assertEquals(BluetoothGattCharacteristic.PROPERTY_READ or BluetoothGattCharacteristic.PROPERTY_NOTIFY,
                (GATT_READABLE or GATT_NOTIFY).getProperty())
        Assert.assertEquals(BluetoothGattCharacteristic.PERMISSION_READ,
                (GATT_READABLE or GATT_NOTIFY).getPermission())
    }
}
