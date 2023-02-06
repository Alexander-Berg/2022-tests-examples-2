package ru.yandex.quasar.fakes

import ru.yandex.quasar.app.common.AudioOutputObservable
import ru.yandex.quasar.app.services.OutputDeviceSwitcher
import ru.yandex.quasar.protobuf.ModelObjects

class FakeOutputDeviceSwitcher(private val audioOutputObservable: AudioOutputObservable) : OutputDeviceSwitcher {
    override fun switchTo(type: ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType) {
        var newValue = audioOutputObservable.current!!
        if (newValue.switchingTo != newValue.currentDevice || newValue.switchingTo == type) {
            return;
        }
        newValue = newValue.toBuilder().setSwitchingTo(type).build()
        audioOutputObservable.receiveValue(newValue)
        newValue = newValue.toBuilder().setCurrentDevice(type).build()
        audioOutputObservable.receiveValue(newValue)
    }

    override fun onCreate() {
    }

    override fun onDestroy() {
    }
}
