package ru.yandex.quasar.shadows

import android.media.session.MediaController
import org.mockito.kotlin.mock
import org.robolectric.annotation.Implements

@Implements(MediaController::class)
class ShadowMediaController {
    val controlsSpy: MediaController.TransportControls = mock()

    fun registerCallback(callback: MediaController.Callback) {}
    fun unregisterCallback(callback: MediaController.Callback) {}
    fun getTransportControls(): MediaController.TransportControls {
        return controlsSpy
    }
}
