package ru.yandex.quasar.app.music

import androidx.test.core.app.ApplicationProvider
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.times
import org.mockito.Mockito.verify
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.core.Configuration
import ru.yandex.quasar.app.services.MediaRequestListener
import ru.yandex.quasar.protobuf.ModelObjects

@RunWith(RobolectricTestRunner::class)
class RadioPlayerTest {
    private lateinit var player: RadioPlayer
    private lateinit var mediaListener: MediaRequestListener

    @Before
    fun init() {
        val configuration: Configuration = mock()
        whenever(configuration.getSoftwareVersion()).thenReturn("xxx")
        mediaListener = mock()
        player = RadioPlayer(
            ApplicationProvider.getApplicationContext(),
            mock(),
            mock(),
            mock(),
            configuration,
            mediaListener,
            mock(),
            mock()
        )
    }

    @Test
    fun when_updateRadioAutostart_should_playMusic() {
        val radio: ModelObjects.Radio = mock()
        whenever(radio.getUrl()).thenReturn("https://somedomain.ru/some")
        player.updateRadio(
            radio,
            false,
            null,
            true
        )
        verify(mediaListener).playMusic()
    }

    @Test
    fun when_updateRadioNoAutostart_should_doNotning() {
        val radio: ModelObjects.Radio = mock();
        whenever(radio.getUrl()).thenReturn("https://somedomain.ru/some")
        player.updateRadio(
            radio,
            false,
            null,
            false
        )
        verify(mediaListener, times(0)).playMusic()
    }
}

