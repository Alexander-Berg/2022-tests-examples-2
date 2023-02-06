package com.google.android.youtube.player

import android.os.Build
import android.os.Bundle
import android.view.ViewGroup
import com.google.android.youtube.player.WrapperYoutubePlayer.PlaybackEventListener
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.anyOrNull
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.MainActivity

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.M])
class WrapperYoutubePlayerImplUnitTest {
    private lateinit var mainActivity: MainActivity
    private lateinit var wrapperYoutubePlayer: WrapperYoutubePlayerImpl
    private lateinit var youTubePlayerView: YouTubePlayerView
    private lateinit var rootLayout: ViewGroup
    private lateinit var youtubePlayerDispatcher: YoutubePlayerDispatcher

    private val playbackEventListener: PlaybackEventListener = mock()

    @Before
    fun init() {
        mainActivity = Robolectric.buildActivity(MainActivity::class.java).get()
        rootLayout = mock()
        youtubePlayerDispatcher = mock()
        whenever(youtubePlayerDispatcher.isInitializing).thenReturn(false)
        whenever(rootLayout.context).thenReturn(mainActivity)
        youTubePlayerView = mock()
        whenever(youTubePlayerView.context).thenReturn(mainActivity)
        whenever(youTubePlayerView.parent).thenReturn(rootLayout)
        wrapperYoutubePlayer = WrapperYoutubePlayerImpl({ youTubePlayerView },
                youtubePlayerDispatcher) // только для юнит-теста, везде должно быть WrapperYoutubePlayerImpl.getInstance()
    }

    @Test
    fun when_initialized_then_loadVideoThrowsNothing() {
        // Arrange
        whenever(youTubePlayerView.a(eq(mainActivity), eq(wrapperYoutubePlayer), any(), any(), anyOrNull()))
            .then {
                wrapperYoutubePlayer.onInitializedListener!!.onInitializationSuccess(wrapperYoutubePlayer, mock<com.google.android.youtube.player.internal.s>(), any())
            }
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)
        // Act
        wrapperYoutubePlayer.loadVideo("ololo")
    }

    @Test
    fun when_initializationFails_then_exceptionIsThrownOnLoadVideo() {
        // Arrange
        whenever(youTubePlayerView.a(eq(mainActivity), eq(wrapperYoutubePlayer), any(), any(), anyOrNull()))
            .then {
                wrapperYoutubePlayer.onInitializedListener!!.onInitializationFailure(wrapperYoutubePlayer, mock())
            }
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)

        // Act
        assertThatThrownBy { wrapperYoutubePlayer.loadVideo("ololo") }.isInstanceOf(IllegalStateException::class.java)
                .hasMessageContaining("YouTube player is not initialized")
    }

    @Test
    fun when_removeAndReinit_then_ok() {
        // Arrange
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)

        // Act
        val result = wrapperYoutubePlayer.onLowMemory()
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)
        // Assert

        assertTrue(result)
    }

    @Test
    fun when_initializationSuccess_then_onInitializationSuccessCalled() {
        // Arrange
        whenever(youTubePlayerView.a(eq(mainActivity), eq(wrapperYoutubePlayer), any(), any(), anyOrNull()))
            .then {
                wrapperYoutubePlayer.onInitializedListener!!.onInitializationSuccess(wrapperYoutubePlayer, mock<com.google.android.youtube.player.internal.s>(), any())
            }
        val onInitializedListener = mock<WrapperYoutubePlayer.OnInitializedListener>()
        wrapperYoutubePlayer.init(rootLayout, onInitializedListener, "", Bundle(), playbackEventListener)

        // Act
        // Assert
        verify(onInitializedListener).onInitializationSuccess(any())
    }

    @Test
    fun when_initializationFailure_then_onInitializationFailureCalled() {
        // Arrange
        whenever(youTubePlayerView.a(eq(mainActivity), eq(wrapperYoutubePlayer), any(), any(), anyOrNull()))
            .then {
                wrapperYoutubePlayer.onInitializedListener!!.onInitializationFailure(wrapperYoutubePlayer, mock())
            }
        val onInitializedListener = mock<WrapperYoutubePlayer.OnInitializedListener>()
        wrapperYoutubePlayer.init(rootLayout, onInitializedListener, "", Bundle(), playbackEventListener)

        // Act
        // Assert
        verify(onInitializedListener).onInitializationFailure(any(), any())
    }

    @Test
    fun when_initializationSuccess_then_bundleIsRestored() {
        // Arrange
        val youTubePlayer = mock<com.google.android.youtube.player.internal.s>()
        whenever(youTubePlayerView.a(eq(mainActivity), eq(wrapperYoutubePlayer), any(), any(), anyOrNull()))
            .then {
                wrapperYoutubePlayer.onInitializedListener!!.onInitializationSuccess(wrapperYoutubePlayer, youTubePlayer, any())
            }
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)

        // Act
        // Assert
        verify(youTubePlayer).a(anyOrNull() as Bundle?) // restoring state of youTubePlayer
    }

    @Test
    fun when_releaseCalled_then_playerIsDestroyed() {
        // Arrange
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)

        // Act
        wrapperYoutubePlayer.release()

        // Assert
        verify(youTubePlayerView).b(true) //YouTubePlayerView destruction
        verify(rootLayout).removeView(youTubePlayerView)
    }

    @Test
    fun when_initCalled_then_oldPlayerIsDestroyed() {
        // Arrange
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)

        // Act
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)

        // Assert
        verify(youTubePlayerView).b(true) //YouTubePlayerView destruction
        verify(rootLayout).removeView(youTubePlayerView)
    }

    @Test
    fun when_initYouTubePlayerViewAlreadyCalled_then_noCallsCanBeProceed() {
        // Arrange
        wrapperYoutubePlayer.init(rootLayout, mock(), "", Bundle(), playbackEventListener)

        // Act
        wrapperYoutubePlayer.a(youTubePlayerView, "", mock())

        // Assert
        verify(youTubePlayerView).a(eq(mainActivity), eq(wrapperYoutubePlayer), any(), any(), anyOrNull())
    }
}

