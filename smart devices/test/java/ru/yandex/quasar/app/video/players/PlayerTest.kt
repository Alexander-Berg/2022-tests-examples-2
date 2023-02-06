package ru.yandex.quasar.app.video.players

import android.os.Bundle
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentCaptor
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.shadows.ShadowLooper
import ru.yandex.quasar.app.alice.AliceStateObservable
import ru.yandex.quasar.app.services.NetworkService
import ru.yandex.quasar.app.video.alice.VideoAliceListener
import ru.yandex.quasar.app.video.telemetry.TvtCounter
import ru.yandex.quasar.app.video.ui.PlayerUI
import ru.yandex.quasar.protobuf.ModelObjects
import java.util.concurrent.TimeUnit


@RunWith(RobolectricTestRunner::class)
class PlayerTest {

    private lateinit var player: TestSubjectPlayer
    private lateinit var playerUI: PlayerUI
    private lateinit var videoBuilder: ModelObjects.Video.Builder
    private lateinit var bundle: Bundle

    @Before
    fun setUp() {
        playerUI = mock()
        bundle = mock()
        videoBuilder = ModelObjects.Video.newBuilder()
    }

    fun init() {
        val video = videoBuilder.build()
        val tvtCounter: TvtCounter = mock()
        player = TestSubjectPlayer(playerUI, video, bundle, tvtCounter, mock())
    }

    @Test
    fun when_onIdle_then_ToFullScreenShouldNotBeCalled() {
        // Arrange
        init()

        // Act
        player.onIdle()

        // Assert
        verify(playerUI, never()).toFullscreen(any())
    }

    @Test
    fun given_videoIsPaused_when_onIdle_then_ToFullScreenShouldNotBeCalled() {
        // Arrange
        init()
        player.stop()

        // Act
        player.onIdle()

        // Assert
        verify(playerUI, never()).toFullscreen(any())
    }

    @Test
    fun when_initCalled_then_initShouldBeDoneCorrectly() {
        // Arrange
        init()
        val networkService: NetworkService = mock()
        val aliceObservable: AliceStateObservable = mock()

        // Act
        player.init(aliceObservable, networkService)

        // Assert
        verify(networkService).setListener(eq(NetworkService.PlayerType.VIDEO), any())
        verify(aliceObservable).addObserver(any())
        assertTrue(player.isInited)
    }

    @Test
    fun when_destroyCalled_then_listenersShouldBeRemoved() {
        // Arrange
        init()
        val networkService: NetworkService = mock()
        val aliceObservable: AliceStateObservable = mock()
        player.init(aliceObservable, networkService)

        // Act
        player.destroy(networkService)


        // Assert
        verify(networkService).removeListener(NetworkService.PlayerType.VIDEO)
        verify(aliceObservable).removeObserver(any())
    }

    @Test
    fun when_weHavePositionAndDurationStored_then_theyAreSetInUiAfterInit() {
        // Arrange
        whenever(bundle.getLong("POSITION")).thenReturn(42000)
        whenever(bundle.getBoolean("PAUSED")).thenReturn(true)
        videoBuilder.setItem(ModelObjects.MediaItem.newBuilder().setDuration(200))
        val video = videoBuilder.build()
        val tvtCounter: TvtCounter = mock()

        // Act
        player = TestSubjectPlayer(playerUI, video, bundle, tvtCounter, mock())

        // Assert
        verify(playerUI).setPosition(42, 200)
    }

    @Test
    fun when_playerIsPaused_then_itSavesStateToBundle() {
        // Arrange
        init()

        // Act
        player.positionMs = 42000
        player.save(bundle)

        // Assert
        verify(bundle).putBoolean("PAUSED", true)
        verify(bundle).putLong("POSITION", 42000)
    }

    @Test
    fun when_playerIsStopped_then_itPausesAndCallsPauseFromPlayerUi() {
        // Arrange
        init()

        // Act
        player.stop()

        // Assert
        verify(playerUI).paused()
        assertTrue(player.isPaused)
    }

    @Test
    fun when_playbackIsResumed_then_itUnpausesAndCallsPlayedFromPlayerUi() {
        // Arrange
        init()
        val networkService: NetworkService = mock()
        val aliceObservable: AliceStateObservable = mock()
        player.init(aliceObservable, networkService)
        player.stop()
        reset(playerUI)

        // Act
        player.resume()


        // Assert
        verify(playerUI).played()
        assertFalse(player.isPaused)
    }

    @Test
    fun given_playbackIsPaused_when_aliceBecomesIdle_then_loadingIndicatorHides() {
        // Arrange
        init()
        val networkService: NetworkService = mock()
        val aliceObservable: AliceStateObservable = mock()
        val captor = ArgumentCaptor.forClass(VideoAliceListener::class.java)
        player.init(aliceObservable, networkService)
        verify(networkService).setListener(eq(NetworkService.PlayerType.VIDEO), captor.capture())
        val aliceListener = captor.value

        // Act
        player.stop()
        aliceListener.idle()
        ShadowLooper.idleMainLooper(1, TimeUnit.SECONDS)


        // Assert
        verify(playerUI, never()).toFullscreen(any())
        verify(playerUI).hideLoading()
    }

    @Test
    fun when_playbackIsStarted_then_previewHides() {
        // Arrange
        init()

        // Act
        player.onLocalStart()

        // Assert
        verify(playerUI).hidePreview()
    }

    @Test
    fun when_playbackHasFinished_then_onVideoEndIsCalledForUi() {
        // Arrange
        init()

        // Act
        player.onVideoEnd()

        // Assert
        verify(playerUI).onVideoEnd()
    }
}
