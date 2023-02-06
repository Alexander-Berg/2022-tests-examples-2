package ru.yandex.quasar.common.ble.fakes

import android.bluetooth.BluetoothGattServer
import android.bluetooth.BluetoothGattServerCallback
import android.bluetooth.BluetoothGattService
import android.bluetooth.BluetoothManager
import android.bluetooth.le.AdvertiseCallback
import android.bluetooth.le.AdvertiseData
import android.bluetooth.le.AdvertiseSettings
import android.bluetooth.le.BluetoothLeAdvertiser
import android.content.Context
import org.mockito.kotlin.mock
import ru.yandex.quasar.common.ble.BleInitializer

class BleInitializerFake(context: Context,
                         private val bluetoothManager: BluetoothManager,
                         private val bleAdvertiser: BluetoothLeAdvertiser,
                         private val gattServer: BluetoothGattServer)
    : BleInitializer(context, mock(), mock()) {

    lateinit var gattServerCallback: BluetoothGattServerCallback
        private set

    lateinit var advertiseCallback: AdvertiseCallback

    override fun init() {
        if(this.onBleReadyCallback != null) {
            this.onBleReadyCallback!!(bluetoothManager, bleAdvertiser)
        }
    }

    override fun openGattServer(callback: BluetoothGattServerCallback): BluetoothGattServer? {
        this.gattServerCallback = callback
        return gattServer
    }

    override fun addGattService(service: BluetoothGattService) {

    }

    override fun startAdvertising(settings: AdvertiseSettings, advertiseData: AdvertiseData,
                                  scanResponse: AdvertiseData, callback: AdvertiseCallback) {
        this.advertiseCallback = callback
    }
}
