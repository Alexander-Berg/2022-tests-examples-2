package ru.yandex.quasar.shadows

import android.content.ComponentName
import android.content.Context
import android.media.browse.MediaBrowser
import android.media.session.MediaSession
import android.os.Bundle
import org.mockito.kotlin.mock
import org.robolectric.annotation.Implementation
import org.robolectric.annotation.Implements

@Implements(MediaBrowser::class)
class ShadowMediaBrowser {

    private lateinit var callback: MediaBrowser.ConnectionCallback
    private var connected = false

    @Implementation
    fun __constructor__(context: Context?, serviceComponent: ComponentName?,
                        callback: MediaBrowser.ConnectionCallback, rootHints: Bundle?) {
        this.callback = callback
    }

    fun connect() {
        connected = true
        this.callback.onConnected()
    }

    fun disconnect() {
        connected = false
    }

    fun isConnected(): Boolean {
        return this.connected
    }

    fun getSessionToken(): MediaSession.Token {
        return mock()
    }
}
