package ru.yandex.quasar.app.video.players

import android.os.Bundle
import com.google.android.youtube.player.WrapperYoutubePlayer
import com.google.android.youtube.player.YouTubePlayer
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentCaptor
import org.mockito.kotlin.any
import org.mockito.kotlin.atLeast
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.video.ui.PlayerUI
import ru.yandex.quasar.protobuf.ModelObjects

@RunWith(RobolectricTestRunner::class)
class YoutubePlayerTest {

    private lateinit var youtubePlayer: YoutubePlayer
    private lateinit var playerUI: PlayerUI
    private lateinit var videoBuilder: ModelObjects.Video.Builder
    private lateinit var bundle: Bundle
    private lateinit var wrapperYoutubePlayer: WrapperYoutubePlayer
    private lateinit var onYoutubePlayerInitializedListener: WrapperYoutubePlayer.OnInitializedListener

    @Before
    fun setUp() {
        playerUI = mock()
        bundle = mock()
        wrapperYoutubePlayer = mock()
        whenever(wrapperYoutubePlayer.pause()).then { youtubePlayer.playbackEventListener.onPaused() }
        videoBuilder = ModelObjects.Video.newBuilder()
    }

    fun init() {
        val video = videoBuilder.build()
        val factory: YoutubePlayerViewFactory = mock()

        val captor = ArgumentCaptor.forClass(WrapperYoutubePlayer.OnInitializedListener::class.java)
        whenever(factory.create(any(), captor.capture(), any(), any(), any())).thenReturn(wrapperYoutubePlayer)
        youtubePlayer = YoutubePlayer(
            playerUI, mock(), video,
            bundle,
            mock(),
            mock(), factory,
            mock(), null
        )
        onYoutubePlayerInitializedListener = captor.value
    }

    @Test
    fun when_initialized_then_loadingIndicatorShowing() {
        // Arrange
        init()

        // Act
        youtubePlayer.init(mock(), mock())

        // Assert
        verify(playerUI, never()).hideLoading()
    }

    @Test
    fun when_notIdle_then_minimizesScreen() {
        // Arrange
        init()
        whenever(playerUI.isFullscreen).thenReturn(true)

        // Act
        youtubePlayer.onNotIdle()

        // Assert
        verify(playerUI).toSmallScreen(any())
    }

    @Test
    fun when_playerIsInitialized_then_videoScreenIsNotShown() {
        // Arrange
        init()

        // Act
        youtubePlayer.init(mock(), mock())

        // Assert
        verify(playerUI, never()).showVideo()
    }

    @Test
    fun when_pauses_then_minimizesScreen() {
        // Arrange
        init()
        whenever(playerUI.isFullscreen).thenReturn(true)

        // Act
        youtubePlayer.onLocalStop()

        // Assert
        verify(playerUI).toSmallScreen(any())
    }

    @Test
    fun when_becomesLoadedAndIdle_then_maximizesScreen() {
        // Arrange
        init()
        youtubePlayer.playbackEventListener.onLoaded("")

        // Act
        youtubePlayer.onIdle()

        // Assert
        verify(playerUI).toFullscreen(any())
    }

    @Test
    fun when_becomesIdleAndLoaded_then_maximizesScreen() {
        // Arrange
        init()
        youtubePlayer.onIdle()

        // Act
        youtubePlayer.playbackEventListener.onLoaded("")

        // Assert
        verify(playerUI).toFullscreen(any())
    }

    @Test
    fun when_becomesLoaded_then_doesntMaximizeScreen() {
        // Arrange
        init()

        // Act
        youtubePlayer.playbackEventListener.onLoaded("")

        // Assert
        verify(playerUI, never()).toFullscreen(any())
    }

    @Test
    fun when_becomesIdle_then_doesntMaximizeScreen() {
        // Arrange
        init()

        // Act
        youtubePlayer.onIdle()

        // Assert
        verify(playerUI, never()).toFullscreen(any())
    }

    @Test
    fun when_videoEnds_then_toSmallScreenCalled() {
        // Arrange
        init()
        whenever(playerUI.isFullscreen).thenReturn(true)

        // Act
        youtubePlayer.playbackEventListener.onVideoEnded()

        // Assert
        verify(playerUI).toSmallScreen(any())
    }

    @Test
    fun when_youTubeErrorOccurs_then_toSmallScreenCalled() {
        // Arrange
        init()
        whenever(playerUI.isFullscreen).thenReturn(true).thenReturn(false)

        // Act
        youtubePlayer.playbackEventListener.onError(YouTubePlayer.ErrorReason.UNKNOWN)

        // Assert
        verify(playerUI).toSmallScreen(any())
    }

    @Test
    fun when_playbackOnStoppedCalled_then_toSmallScreenCalled() {
        // Arrange
        init()
        whenever(playerUI.isFullscreen).thenReturn(true)

        // Act
        youtubePlayer.playbackEventListener.onStopped()

        // Assert
        verify(playerUI).toSmallScreen(any())
    }

    @Test
    fun given_playbackIsPaused_when_becomesIdleAndLoaded_then_loadingIndicatorHides() {
        // Arrange
        whenever(bundle.getBoolean("PAUSED")).thenReturn(true)
        init()

        // Act
        youtubePlayer.onIdle()
        youtubePlayer.playbackEventListener.onLoaded("")

        // Assert
        verify(playerUI, atLeast(1)).hideLoading()
    }

    @Test
    fun when_seekToCalled_then_youtubePlayerSeeksToThatPosition() {
        // Arrange
        init()
        onYoutubePlayerInitializedListener.onInitializationSuccess(wrapperYoutubePlayer)

        // Act
        youtubePlayer.seekTo(42042)

        // Assert
        verify(wrapperYoutubePlayer).seekTo(42042)
    }

    @Test
    fun given_youtubePlayerHasInitialized_when_getPositionCalled_then_youtubePlayerIsQueriedForIt() {
        // Arrange
        init()
        onYoutubePlayerInitializedListener.onInitializationSuccess(wrapperYoutubePlayer)
        whenever(wrapperYoutubePlayer.currentTimeMillis).thenReturn(42042)

        // Act
        val posMs = youtubePlayer.positionMs
        val posSec = youtubePlayer.positionSec

        // Assert
        Assert.assertEquals(42042, posMs)
        Assert.assertEquals(42, posSec)
    }

    @Test
    fun given_youtubePlayerHasInitialized_when_getDurationCalled_then_youtubePlayerIsQueriedForIt() {
        // Arrange
        init()
        onYoutubePlayerInitializedListener.onInitializationSuccess(wrapperYoutubePlayer)
        whenever(wrapperYoutubePlayer.durationMillis).thenReturn(42042)

        // Act
        val durMs = youtubePlayer.durationMs
        val durSec = youtubePlayer.durationSec

        // Assert
        Assert.assertEquals(42042, durMs)
        Assert.assertEquals(42, durSec)
    }

    @Test
    fun when_onUiStartCalled_then_itsForwardedToWrapperYoutubePlayer() {
        // Arrange
        init()

        // Act
        youtubePlayer.onUiStart()

        // Assert
        verify(wrapperYoutubePlayer).onStart()
    }

    @Test
    fun when_onUiResumeCalled_then_itsForwardedToWrapperYoutubePlayer() {
        // Arrange
        init()

        // Act
        youtubePlayer.onUiResume()

        // Assert
        verify(wrapperYoutubePlayer).onResume()
    }

    @Test
    fun when_onUiPauseCalled_then_itsForwardedToWrapperYoutubePlayer() {
        // Arrange
        init()

        // Act
        youtubePlayer.onUiPause()

        // Assert
        verify(wrapperYoutubePlayer).onPause()
    }

    @Test
    fun when_onUiStopCalled_then_itsForwardedToWrapperYoutubePlayer() {
        // Arrange
        init()

        // Act
        youtubePlayer.onUiStop()

        // Assert
        verify(wrapperYoutubePlayer).onStop()
    }

    @Test
    fun when_saveCalled_then_itsForwardedToWrapperYoutubePlayer() {
        // Arrange
        init()

        // Act
        youtubePlayer.save(bundle)

        // Assert
        verify(wrapperYoutubePlayer).save(eq(bundle))
    }

    @Test
    fun given_bundleHasPositionSaved_when_videoLoads_then_itSkipsToThisPosition() {
        // Arrange
        videoBuilder.setItem(ModelObjects.MediaItem.newBuilder().setItemId("itemId"))
        whenever(wrapperYoutubePlayer.currentTimeMillis).thenReturn(42000)
        init()

        // Act
        youtubePlayer.loadVideo(wrapperYoutubePlayer)

        // Assert
        verify(wrapperYoutubePlayer).loadVideo("itemId", 42000)
    }

    @Test
    fun given_noPreferredPositionsToStart_when_videoLoads_then_itStartsFromTheBeginning() {
        // Arrange
        videoBuilder.setItem(ModelObjects.MediaItem.newBuilder().setItemId("itemId"))
        init()

        // Act
        youtubePlayer.loadVideo(wrapperYoutubePlayer)

        // Assert
        verify(wrapperYoutubePlayer, times(1)).loadVideo("itemId")
    }
}
