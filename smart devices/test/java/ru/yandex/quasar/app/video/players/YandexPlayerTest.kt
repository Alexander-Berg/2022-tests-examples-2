package ru.yandex.quasar.app.video.players

import android.os.Bundle
import android.widget.FrameLayout
import com.yandex.yabroview.YabroSurfaceView
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.shadows.ShadowLooper
import ru.yandex.quasar.TestUtils.toJsonQuotes
import ru.yandex.quasar.app.auth.AuthObservable
import ru.yandex.quasar.core.MetricaReporter
import ru.yandex.quasar.app.video.players.configurators.YandexPlayerConfigurator
import ru.yandex.quasar.app.video.telemetry.TvtCounter
import ru.yandex.quasar.app.video.ui.PlayerUI
import ru.yandex.quasar.fakes.FakeConfiguration
import ru.yandex.quasar.protobuf.ModelObjects
import java.util.concurrent.TimeUnit

class TestSubjectPlayer(playerUI: PlayerUI,
                        video: ModelObjects.Video,
                        bundle: Bundle,
                        tvtCounter: TvtCounter,
                        metricaReporter: MetricaReporter
) :
        Player(playerUI, video, bundle, tvtCounter, metricaReporter) {
    override fun seekTo(positionMs: Long) {
    }

    override fun setVolume(volume: Float) {
    }

    override fun contentReady(): Boolean {
        return true
    }

    override fun supportsBackgroundTransparency(): Boolean {
        return true
    }

    override fun updatePlayerPosition() {
    }

}

@RunWith(RobolectricTestRunner::class)
class YandexPlayerTest {

    private lateinit var yandexPlayer: YandexPlayer
    private lateinit var playerUI: PlayerUI
    private lateinit var videoBuilder: ModelObjects.Video.Builder
    private lateinit var bundle: Bundle
    private lateinit var authObservable: AuthObservable
    private lateinit var yabroView: YabroSurfaceView
    private lateinit var playerRoot: FrameLayout

    @Before
    fun setUp() {
        playerUI = mock()
        bundle = mock()
        videoBuilder = ModelObjects.Video.newBuilder()
        authObservable = mock()
        yabroView = mock()
        playerRoot = mock()
    }

    fun init() {
        val video = videoBuilder.build()
        val configurator: YandexPlayerConfigurator = mock()
        val configuration = FakeConfiguration()
        configuration.initialize(toJsonQuotes("{'common': {'yaBroViewWrapperUrl': 'some_url'}}"))
        whenever(configurator.create(any(), any())).thenReturn(yabroView)
        yandexPlayer = YandexPlayer(mock(), playerUI, playerRoot, video,
                bundle,
                mock(),
                authObservable, mock(), configuration, configurator)
    }

    @Test
    fun when_playerIsInitialized_then_videoScreenIsNotShownUntilPageIsLoaded() {
        /* If we show YaBro before the page is loaded, we will see a white screen for a couple of seconds, we do not want it. */

        // Arrange
        init()

        // Act
        yandexPlayer.init(mock(), mock())

        // Assert
        verify(playerUI, never()).showVideo()
    }

    @Test
    fun when_notIdle_then_shouldNotMinimizeScreen() {
        // Arrange
        init()

        // Act
        yandexPlayer.onNotIdle()
        ShadowLooper.idleMainLooper(1, TimeUnit.SECONDS)

        // Assert
        verify(playerUI, never()).toSmallScreen(any())
    }

    @Test
    fun when_videoIsPaused_then_javascriptGetsPauseCommand() {
        // Arrange
        init()

        // Act
        yandexPlayer.onLocalStop()

        // Arrange
        verify(yabroView).evaluateJavascript("player.pause()", null)
        verify(playerUI).pausePlay(yandexPlayer, false)
    }

    @Test
    fun when_videoIsResumed_then_javascriptGetsResumeCommand() {
        // Arrange
        init()

        // Act
        yandexPlayer.onLocalStart()

        // Arrange
        verify(yabroView).evaluateJavascript("player.resume()", null)
    }

    @Test
    fun when_replayIsRequested_then_positionIsSetToZeroAndYabroIsReloaded() {
        // Arrange
        whenever(bundle.getLong("POSITION")).thenReturn(4242)
        init()

        // Act
        yandexPlayer.replay()

        // Assert
        Assert.assertEquals(0, yandexPlayer.positionSec)
        verify(yabroView).reload()
    }

    @Test
    fun when_playerIsDestroyed_then_yabroIsDestroyedAndPlayerIsRemovedFromView() {
        // Arrange
        init()

        // Act
        yandexPlayer.destroy(mock())

        // Assert
        verify(yabroView).destroy()
        verify(playerRoot).removeView(yabroView)
    }

    @Test
    fun when_playerSeeked_then_javascriptGetsSetCurrentTimeCommand() {
        // Arrange
        init()

        // Act
        yandexPlayer.seekTo(42042)

        // Arrange
        verify(yabroView).evaluateJavascript("player.setCurrentTime(42)", null)
        Assert.assertEquals(42042, yandexPlayer.positionMs)
    }

    @Test
    fun when_volumeIsSet_then_javascriptGetsSetVolumeCommand() {
        // Arrange
        init()

        // Act
        yandexPlayer.setVolume(5f)

        // Arrange
        verify(yabroView).evaluateJavascript("player.setVolume(500.0)", null)
    }
}
