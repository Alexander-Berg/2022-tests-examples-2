package ru.yandex.quasar.app.video.players

import android.content.Context
import android.os.Bundle
import android.widget.FrameLayout
import com.google.android.exoplayer2.ExoPlaybackException
import com.google.android.exoplayer2.ui.PlayerView
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentCaptor
import org.mockito.ArgumentMatchers.anyInt
import org.mockito.ArgumentMatchers.anyLong
import org.mockito.kotlin.any
import org.mockito.kotlin.atLeastOnce
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.auth.AuthObservable
import ru.yandex.quasar.core.Configuration
import ru.yandex.quasar.core.MetricaReporter
import ru.yandex.quasar.fakes.FakeConfiguration
import ru.yandex.quasar.app.utils.HttpClient
import ru.yandex.quasar.app.video.players.configurators.YandexPlayerBasedConfigurator
import ru.yandex.quasar.app.video.telemetry.TvtCounter
import ru.yandex.quasar.app.video.ui.PlayerUI
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.util.NetUtil
import ru.yandex.video.data.dto.VideoData
import ru.yandex.video.player.PlaybackException
import java.io.IOException
import java.lang.Exception

class TestSubjectHeadlessYandexPlayerBasedVideoPlayer(
    context: Context,

    playerUI : PlayerUI,
    playerRoot: FrameLayout,
    video : ModelObjects.Video,
    bundle: Bundle,
    tvtCounter: TvtCounter,
    authObservable: AuthObservable,
    httpClient: HttpClient,
    metricaReporter: MetricaReporter,
    configuration: Configuration,
    configurator: YandexPlayerBasedConfigurator<VideoData>,
    netUtil: NetUtil)
    : YandexPlayerBasedVideoPlayer<VideoData>(context, "", playerUI, playerRoot, video,
        bundle, tvtCounter, authObservable, httpClient, metricaReporter, configuration,
        configurator, netUtil, mock(), null) {
}

@RunWith(RobolectricTestRunner::class)
class YandexPlayerBasedVideoPlayerTest {

    private lateinit var player: TestSubjectHeadlessYandexPlayerBasedVideoPlayer
    private lateinit var playerUi: PlayerUI
    private lateinit var videoBuilder: ModelObjects.Video.Builder
    private lateinit var playerElement: ru.yandex.video.player.YandexPlayer<com.google.android.exoplayer2.Player>
    private lateinit var configurator: YandexPlayerBasedConfigurator<VideoData>
    private lateinit var bundle: Bundle
    private lateinit var videoData: VideoData
    private lateinit var fakeConfiguration: FakeConfiguration
    private lateinit var playerRoot: FrameLayout
    private lateinit var exoPlayer: com.google.android.exoplayer2.Player
    private lateinit var exoPlayerView: PlayerView

    @Before
    fun setUp() {
        playerUi = mock()
        videoBuilder = ModelObjects.Video.newBuilder()
        bundle = mock()
        videoData = mock()
        playerRoot = mock()
        configurator = mock() as YandexPlayerBasedConfigurator<VideoData>

        fakeConfiguration = FakeConfiguration()
        fakeConfiguration.initialize("{'mediad': {'metrica_logger_enabled': false }}")

        playerElement = mock() as ru.yandex.video.player.YandexPlayer<com.google.android.exoplayer2.Player>

        exoPlayer = mock()
        exoPlayerView = mock()
        whenever(playerRoot.findViewById<PlayerView>(anyInt())).thenReturn(exoPlayerView)

        whenever(configurator.create(any(), any(), any())).thenReturn(playerElement)
        whenever(configurator.videoData).thenReturn(videoData)
    }

    fun init() {
        val video = videoBuilder.build()
        player = TestSubjectHeadlessYandexPlayerBasedVideoPlayer(mock(),
            playerUi,
            playerRoot,
            video,
            bundle,
            mock(),
            mock(),
            mock(),
            mock(),
            fakeConfiguration,
            configurator,
            mock()
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

    @Test
    fun when_seekTo_called_then_setsNewPositionInUi() {
        // Arrange
        init()

        // Act
        player.seekTo(4242000)

        // Assert
        verify(playerUi).setPosition(4242, 0)
        verify(playerElement).seekTo(4242000)
        Assert.assertEquals(4242000, player.positionMs)
    }

    @Test
    fun when_attachToUi_called_then_subscribeSelfToPlayerElementEvents() {
        // Act
        init()

        // Assert
        verify(playerElement).addObserver(player)
    }

    @Test(expected = VideoPlayPayloadException::class)
    fun given_configuratorThrowsException_when_creatingPlayerElement_then_exceptionIsRethrown() {
        // Arrange
        whenever(configurator.create(any(), any(), any())).thenThrow(VideoPlayPayloadException("error"))

        // Act
        val video = videoBuilder.build()
        player = TestSubjectHeadlessYandexPlayerBasedVideoPlayer(
            mock(),
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
            mock()
        )

        // Assert

        /* Nothing here, as we utilize the 'expected' property of @Test attribute to check that
            exception is thrown */
    }

    @Test
    fun given_configuratorThrowsException_when_creatingPlayerElement_then_stopsPlayerAndUi() {
        // Arrange
        whenever(configurator.create(any(), any(), any())).thenThrow(VideoPlayPayloadException("error"))
        var threw = false

        // Act
        try {
            val video = videoBuilder.build()
            player = TestSubjectHeadlessYandexPlayerBasedVideoPlayer(mock(),
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
                mock()
            )
        } catch(e: VideoPlayPayloadException) {
            threw = true
        }

        // Assert
        Assert.assertTrue(threw)
        verify(playerUi).paused()
        verify(playerUi).onPlayerError(any(), eq(false))
    }

    @Test
    fun when_getLiveEdgePosition_called_then_returnsLiveEdgePositionFromYandexPlayerElement() {
        // Arrange
        whenever(playerElement.getLiveEdgePosition()).thenReturn(42)
        init()

        // Act
        val pos = player.liveEdgePosition

        // Assert
        Assert.assertEquals(42, pos)
    }

    @Test
    fun given_bundleHasSavedPosition_when_init_then_playerElementSeeksToThisPosition_and_preparesYandexPlayerElement() {
        // Arrange
        whenever(bundle.getLong("POSITION")).thenReturn(42000)
        init()

        // Act
        player.init(mock(), mock())

        // Assert
        verify(playerElement).seekTo(42000)
        verify(playerElement).prepare(
                eq(videoData),
                eq(42000L),
                eq(false))
    }

    @Test
    fun given_bundleDoesntHaveSavedPosition_when_init_then_playerElementDoesntSeekToAnyPosition_and_preparesYandexPlayerElement() {
        // Arrange
        init()

        // Act
        player.init(mock(), mock())

        // Assert
        verify(playerElement, never()).seekTo(anyLong())
        verify(playerElement).prepare(
                eq(videoData),
                eq(null),
                eq(false))
    }

    @Test
    fun when_playerIsDestroyed_then_YandexPlayerElementIsReleased() {
        // Arrange
        init()

        // Act
        player.destroy(mock())

        // Assert
        verify(playerElement).release()
    }

    @Test
    fun when_playbackIsStarted_then_previewHides() {
        // Arrange
        init()

        // Act
        player.onLocalStart()

        // Assert
        verify(playerUi).hidePreview()
    }

    @Test
    fun when_playbackIsStarted_then_YandexPlayerElementStartsPlayback() {
        // Arrange
        init()

        // Act
        player.onLocalStart()

        // Assert
        verify(playerElement).play()
    }

    @Test
    fun given_videoHasPlaybackAndDuration_when_playbackIsStopped_then_internalProgressIsUpdated() {
        // Arrange
        whenever(playerElement.getPosition()).thenReturn(42000)
        whenever(playerElement.getAvailableWindowDuration()).thenReturn(200000)
        init()
        player.init(mock(), mock())

        // Act
        player.onLocalStop()

        // Assert
        Assert.assertEquals(42000, player.positionMs)
        Assert.assertEquals(200000, player.durationMs)
    }

    @Test
    fun when_playerIsInitialized_then_videoScreenIsShownImmediately() {
        // Arrange
        init()

        // Act
        player.init(mock(), mock())

        // Assert
        verify(playerUi).showVideo()
    }

    @Test
    fun when_playbackIsStopped_then_YandexPlayerElementIsPaused() {
        // Arrange
        init()
        player.init(mock(), mock())

        // Act
        player.onLocalStop()

        // Assert
        verify(playerElement).pause()
    }

    @Test
    fun when_playbackIsStopped_then_UiTransitsToPauseState() {
        // Arrange
        init()
        player.init(mock(), mock())

        // Act
        player.onLocalStop()

        // Assert
        verify(playerUi).pausePlay(eq(player), eq(true))
    }

    @Test
    fun when_YandexPlayerElementBufferedAheadOfCurrentPosition_then_contentIsConsideredReady() {
        // Arrange
        whenever(playerElement.getPosition()).thenReturn(50000)
        whenever(playerElement.getBufferedPosition()).thenReturn(50001)
        init()

        // Act
        val ready = player.contentReady()

        // Assert
        Assert.assertTrue(ready)
    }

    @Test
    fun when_YandexPlayerElementBufferedBehindOfCurrentPosition_then_contentIsConsideredReady() {
        // Arrange
        whenever(playerElement.getPosition()).thenReturn(50000)
        whenever(playerElement.getBufferedPosition()).thenReturn(49999)
        init()

        // Act
        val ready = player.contentReady()

        // Assert
        Assert.assertFalse(ready)
    }

    @Test
    fun when_YandexPlayerElementBufferedEqualToCurrentPosition_then_contentIsConsideredReady() {
        // Arrange
        whenever(playerElement.getPosition()).thenReturn(50000)
        whenever(playerElement.getBufferedPosition()).thenReturn(50000)
        init()

        // Act
        val ready = player.contentReady()

        // Assert
        Assert.assertFalse(ready)
    }

    @Test
    fun when_hidedPlayerIsReady_then_playerIsAttachedToVew() {
        // Arrange
        val exoPlayer: com.google.android.exoplayer2.Player = mock()
        val exoPlayerView: PlayerView = mock()
        whenever(playerRoot.findViewById<PlayerView>(anyInt())).thenReturn(exoPlayerView)
        fakeConfiguration.initialize("{'mediad': {'metrica_logger_enabled': false }}")
        init()

        // Act
        player.onHidedPlayerReady(exoPlayer)

        // Assert
        verify(exoPlayerView).setPlayer(eq(exoPlayer))
    }

    @Test
    fun when_YandexPlayerElementFiresError_then_uiTransitionsToPausedState() {
        // Arrange
        init()

        player.onHidedPlayerReady(exoPlayer)

        val captor = ArgumentCaptor.forClass(com.google.android.exoplayer2.Player.EventListener::class.java)
        verify(exoPlayer, atLeastOnce()).addListener(captor.capture())
        val listener = captor.value

        // Act
        listener.onPlayerError(ExoPlaybackException.createForSource(IOException()))

        // Assert
        verify(playerUi).pausePlay(eq(player), eq(false))
    }

    @Test
    fun when_setVolumeCalled_then_volumeIsSetForExoPlayer() {
        // Arrange
        init()

        player.onHidedPlayerReady(exoPlayer)
        val audioComponent: com.google.android.exoplayer2.Player.AudioComponent = mock()
        whenever(exoPlayer.audioComponent).thenReturn(audioComponent)

        // Act
        player.setVolume(66.5F)

        // Assert
        verify(audioComponent).setVolume(66.5F)
    }

    @Test
    fun when_playbackEnded_then_uiCallbackIsCalledAndLoadingIndicatorHides() {
        // Arrange
        init()

        // Act
        player.onPlaybackEnded()

        // Assert
        verify(playerUi).onVideoEnd()
        verify(playerUi).hideLoading()
    }

    @Test
    fun when_LoadingStarts_then_uiShowsLoadingIndicator() {
        // Arrange
        init()

        // Act
        player.onLoadingStart()

        // Assert
        verify(playerUi).showLoading()
    }

    @Test
    fun when_LoadingFinishes_then_uiHidesLoadingIndicator() {
        // Arrange
        init()

        // Act
        player.onLoadingFinished ()

        // Assert
        verify(playerUi).hideLoading()
    }

    @Test
    fun when_paybackErrorOccurs_then_uiTransitionsToPauseState() {
        // Arrange
        whenever(playerUi.getResourceString(anyInt())).thenReturn("error message")

        init()

        // Act
        player.onPlaybackError(mock())

        // Assert
        verify(playerUi).paused()
    }

    @Test
    fun when_playbackErrorOccurs_then_uiShowsErrorMessage() {
        // Arrange
        whenever(playerUi.getResourceString(anyInt())).thenReturn("error message")

        init()

        // Act
        player.onPlaybackError(PlaybackException.ErrorQueryingDecoders(Exception()))

        // Assert
        verify(playerUi).onPlayerError(any(), eq(false))
    }

    @Test
    /* QUASAR-6417 */
    fun given_playerIsNotReadyYet_when_onFullscreenIsCalled_then_playIsNotCalledYet() {
        // Arrange
        init()

        // Act
        player.onFullscreen()

        // Assert
        verify(playerElement, never()).play()
    }

    @Test
    /* QUASAR-6417 */
    fun when_onHidedPlayerIsReady_then_playIsCalled() {
        // Arrange
        init()

        // Act
        player.onHidedPlayerReady(exoPlayer)

        // Assert
        verify(playerElement).play()
    }

    @Test
    /* QUASAR-6417 */
    fun given_playerIsReady_when_onFullscreenIsCalled_then_playIsCalled() {
        // Arrange
        init()
        player.onFullscreen()
        player.onHidedPlayerReady(exoPlayer)
        reset(playerElement)

        // Act
        player.onFullscreen()

        // Assert
        verify(playerElement).play()
    }
}


