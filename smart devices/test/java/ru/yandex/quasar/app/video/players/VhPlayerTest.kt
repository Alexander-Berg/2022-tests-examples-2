package ru.yandex.quasar.app.video.players

import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.*
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.video.players.configurators.VhPlayerConfigurator
import ru.yandex.quasar.app.video.ui.PlayerUI
import ru.yandex.quasar.fakes.FakeConfiguration
import ru.yandex.quasar.protobuf.ModelObjects

@RunWith(RobolectricTestRunner::class)
class VhPlayerTest {

    private lateinit var player: VhPlayer
    private lateinit var playerUi: PlayerUI
    private lateinit var videoBuilder: ModelObjects.Video.Builder

    @Before
    fun setUp() {
        playerUi = mock()
        videoBuilder = ModelObjects.Video.newBuilder()
    }

    fun init() {
        val video = videoBuilder.build()
        val configurator: VhPlayerConfigurator = mock()
        whenever(configurator.create(any(), any(), any())).thenReturn(mock())

        player = VhPlayer(mock(),
            playerUi,
            mock(),
            video,
            mock(),
            mock(),
            mock(),
            mock(),
            mock(),
            FakeConfiguration(),
            configurator,
            mock(),
            mock(),
            null
        )
    }


    @Test
    fun when_loadingStarts_then_loadingIndicatorShows() {
        // Arrange
        init()

        // Act
        player.onLoadingStart()

        // Assert
        verify(playerUi).showLoading()
    }
}


