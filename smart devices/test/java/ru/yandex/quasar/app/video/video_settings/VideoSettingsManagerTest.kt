package ru.yandex.quasar.app.video.video_settings

import android.os.Handler
import android.view.View
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.atLeastOnce
import org.mockito.kotlin.clearInvocations
import org.mockito.kotlin.eq
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.alice.AliceStateObservable
import ru.yandex.quasar.app.alice.views.VideoControlPanelView
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.protobuf.ModelObjects.AliceState
import ru.yandex.quasar.shadows.ShadowLogger
import ru.yandex.quasar.view.PlayerCoverView
import ru.yandex.quasar.view.views.SpeechView

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowLogger::class], instrumentedPackages = ["ru.yandex.quasar.util"])
class VideoSettingsManagerTest {
    private val fakeMetricaReporter = FakeMetricaReporter()
    private val mockHandler: Handler = mock()
    private val isPlayerPaused = { playerPaused }
    private val resumePlayer = { isPlayerResumed = true }
    private val videoSettingsView: VideoSettingsView = mock()
    private val speechView: SpeechView = mock()
    private val playerCoverView: PlayerCoverView = mock()
    private val videoControlPanelView: VideoControlPanelView = mock()
    private val aliceStateObservable = AliceStateObservable(mock())
    private var playerPaused = false
    private var isPlayerResumed = false
    private var isVideoSettingsVisible = false

    @Before
    fun setUp() {
        whenever(videoSettingsView.visibility).thenReturn(if (isVideoSettingsVisible) View.VISIBLE else View.GONE)
    }


    private fun createManager(): VideoSettingsManager {
        return VideoSettingsManager(
            mock(),
            videoSettingsView,
            mock(),
            speechView,
            videoControlPanelView,
            isPlayerPaused,
            resumePlayer,
            mockHandler,
            fakeMetricaReporter,
            aliceStateObservable,
            mock(),
            playerCoverView,
            false,
            mock(),
            mock()
        )
    }

    private fun runPostDelayed() {
        argumentCaptor<Runnable> {
            verify(mockHandler, atLeastOnce()).postDelayed(capture(), any())
            for (runnable in allValues) {
                runnable.run()
            }
        }
    }

    private fun runPost() {
        argumentCaptor<Runnable> {
            verify(mockHandler, atLeastOnce()).post(capture())
            for (runnable in allValues) {
                runnable.run()
            }
        }
    }

    @Test
    fun given_visibilityManager_when_showVideoSettings_then_settingsIsVisible() {
        val manager = createManager()
        manager.showVideoSettings()
        argumentCaptor<Int> {
            verify(videoSettingsView).visibility = capture()
            val visibility = firstValue
            assertEquals(View.VISIBLE, visibility)
        }
    }

    @Test
    fun given_visibilityManager_when_showVideoSettings_then_eventHasBeenSent() {
        val manager = createManager()
        manager.showVideoSettings()
        assertEquals(1, fakeMetricaReporter.events.size)
        assertEquals(
            VideoSettingsManager.VIDEO_SETTINGS_SHOWN,
            fakeMetricaReporter.events.first().name
        )
    }

    @Test
    fun given_visibilityManager_when_showVideoSettings_then_hidingWasScheduled() {
        val manager = createManager()
        manager.showVideoSettings()
        verify(mockHandler).postDelayed(
            any(),
            eq(VideoSettingsManager.HIDE_VIDEO_SETTINGS_IN_MS)
        )
    }


    @Test
    fun given_shownVideoSettings_when_showVideoSettingsAgain_then_previousHidingWasCancelled() {
        val manager = createManager()
        manager.showVideoSettings()

        manager.showVideoSettings()

        inOrder(mockHandler) {
            verify(mockHandler).postDelayed(
                any(),
                eq(VideoSettingsManager.HIDE_VIDEO_SETTINGS_IN_MS)
            )
            verify(mockHandler).removeCallbacksAndMessages(null)
            verify(mockHandler).postDelayed(
                any(),
                eq(VideoSettingsManager.HIDE_VIDEO_SETTINGS_IN_MS)
            )
        }
    }

    @Test
    fun given_visibilityManager_when_runHiding_then_eventHasBeenSent() {
        val manager = createManager()
        manager.showVideoSettings()

        // hide video settings by timer
        runPostDelayed()

        assertEquals(2, fakeMetricaReporter.events.size)
        assertEquals(
            VideoSettingsManager.VIDEO_SETTINGS_HIDDEN,
            fakeMetricaReporter.events.last().name
        )
    }

    @Test
    fun given_shownVideoSettings_when_runHiding_then_previousHidingWasCancelled() {
        val manager = createManager()
        manager.showVideoSettings()

        // hide video settings by timer
        runPostDelayed()

        verify(mockHandler).removeCallbacksAndMessages(null)
    }

    @Test
    fun given_visibilityManager_when_showSettings_then_suggestsShown() {
        val manager = createManager()

        manager.showVideoSettings()

        verify(speechView).setStationSuggestStrings(any())
        argumentCaptor<Boolean> {
            verify(videoControlPanelView).hideSuggestsOnIdle(capture(), any())
            assertTrue(firstValue)
        }
    }

    @Test
    fun given_shownVideoSettings_when_runHiding_then_suggestsHidden() {
        val manager = createManager()

        manager.showVideoSettings()
        clearInvocations(speechView)
        clearInvocations(videoControlPanelView)

        runPostDelayed()

        verify(speechView).setStationSuggestStrings(listOf())
        argumentCaptor<Boolean> {
            verify(videoControlPanelView).hideSuggestsOnIdle(capture(), eq(true))
            assertFalse(firstValue)
        }
    }

    @Test
    fun given_shownVideoSettings_when_runHiding_then_settingsIsHidden() {
        val manager = createManager()
        manager.showVideoSettings()

        runPostDelayed()

        argumentCaptor<Int> {
            verify(videoSettingsView, times(2)).visibility = capture()
            val visibility = secondValue
            assertEquals(View.GONE, visibility)
        }
    }

    @Test
    fun given_playerIsPaused_when_showVideoSettings_then_playerWillNotBeResumed() {
        val manager = createManager()
        playerPaused = true
        manager.showVideoSettings()

        runPostDelayed()

        assert(!isPlayerResumed)
    }

    @Test
    fun given_playerIsNotPaused_when_showVideoSettings_then_playerResumed() {
        val manager = createManager()
        playerPaused = false
        manager.showVideoSettings()

        runPostDelayed()

        assert(isPlayerResumed)
    }

    @Test
    fun given_shownVideoSettings_when_playerPaused_then_playerWillNotBeResumed() {
        val manager = createManager()
        manager.showVideoSettings()

        playerPaused = true
        runPostDelayed()

        assert(!isPlayerResumed)
    }

    @Test
    fun given_shownVideoSettings_when_aliceStateIsBusy_then_settingsAreNotHidden() {
        val manager = createManager()
        manager.showVideoSettings()

        val message = AliceState.newBuilder().setState(AliceState.State.BUSY).build()
        aliceStateObservable.receiveValue(message)
        runPost()

        argumentCaptor<Int> {
            verify(videoSettingsView).visibility = capture()
            val visibility = firstValue
            assertEquals(View.VISIBLE, visibility)
        }
    }

    @Test
    fun given_shownVideoSettings_when_aliceStateIsSpeaking_then_settingsHidden() {
        val manager = createManager()
        manager.showVideoSettings()
        whenever(videoSettingsView.visibility).thenReturn(View.VISIBLE)

        val message = AliceState.newBuilder().setState(AliceState.State.SPEAKING).build()
        aliceStateObservable.receiveValue(message)
        runPost()

        argumentCaptor<Int> {
            verify(videoSettingsView, times(2)).visibility = capture()
            val visibility = secondValue
            assertEquals(View.GONE, visibility)
        }
    }

    @Test
    fun given_shownVideoSettings_when_endListeningToSpeech_then_settingsScheduledToHide() {
        val manager = createManager()
        manager.showVideoSettings()
        whenever(videoSettingsView.visibility).thenReturn(View.VISIBLE)

        val listening = AliceState.newBuilder()
            .setState(AliceState.State.LISTENING)
            .setRecognizedPhrase("Not empty phrase")
            .build()
        val idle =  AliceState.newBuilder().setState(AliceState.State.IDLE).build()
        aliceStateObservable.receiveValue(listening)
        aliceStateObservable.receiveValue(idle)
        runPost()

        verify(mockHandler).postDelayed(any(), eq(VideoSettingsManager.HIDE_VIDEO_SETTINGS_AFTER_REQUEST_IN_MS))
    }

    @Test
    fun given_shownVideoSettings_when_aliceStateIsNotIdle_then_settingsIsNotHiddenByTimer() {
        val manager = createManager()
        manager.showVideoSettings()

        val message = AliceState.newBuilder().setState(AliceState.State.LISTENING).build()
        aliceStateObservable.receiveValue(message)
        runPost()
        runPostDelayed()

        argumentCaptor<Int> {
            verify(videoSettingsView).visibility = capture()
            val visibility = firstValue
            assertEquals(View.VISIBLE, visibility)
        }
    }

    @Test
    fun given_shownVideoSettings_when_aliceIsIdle_then_settingsAreNotHidden() {
        val manager = createManager()
        manager.showVideoSettings()
        whenever(videoSettingsView.visibility).thenReturn(View.VISIBLE)

        val message = AliceState.newBuilder().setState(AliceState.State.IDLE).build()
        aliceStateObservable.receiveValue(message)
        runPost()

        argumentCaptor<Int> {
            verify(videoSettingsView).visibility = capture()
            val visibility = firstValue
            assertEquals(View.VISIBLE, visibility)
        }
    }

    @Test
    fun given_shownVideoSettings_when_aliceStateBecomeIdle_then_settingsHidden() {
        val manager = createManager()
        var message = AliceState.newBuilder().setState(AliceState.State.LISTENING).build()

        manager.showVideoSettings()
        whenever(videoSettingsView.visibility).thenReturn(View.VISIBLE)
        // Alice is not idle, so settings still shown
        aliceStateObservable.receiveValue(message)
        runPost()
        runPostDelayed()
        clearInvocations(mockHandler)

        // Alice become idle and video settings has to be hidden
        message = AliceState.newBuilder().setState(AliceState.State.IDLE).build()
        aliceStateObservable.receiveValue(message)
        runPost()

        argumentCaptor<Int> {
            verify(videoSettingsView, times(2)).visibility = capture()
            val visibility = secondValue
            assertEquals(View.GONE, visibility)
        }
    }
}
