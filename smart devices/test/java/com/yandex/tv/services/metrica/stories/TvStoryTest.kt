package com.yandex.tv.services.metrica.stories
import android.os.Bundle
import com.yandex.tv.services.metrica.Events
import com.yandex.tv.services.metrica.Keys
import com.yandex.tv.services.metrica.StoryEvent
import com.yandex.tv.services.metrica.stories.util.DeviceICookieHolder
import com.yandex.tv.services.metrica.stories.util.SessionIdProvider
import com.yandex.tv.services.metrica.stories.util.StartupPlaceTracker
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class TvStoryTest {

    private val fromTvApp = "tv-app"
    private val fromInputServiceApp = "input-service-app"
    private var channelId = "1"
    private val uuid = "ff11"
    private val deviceId = "aa00"
    private val sessionId = "33dd"
    private var startTime = 1644500000000L
    private var currentTime = startTime
    private var eventNum = 0
    private var singleScreenSessionIdProvider = Mockito.mock(SessionIdProvider::class.java)
    private var startupPlaceTracker = Mockito.mock(StartupPlaceTracker::class.java)
    private var iCookieHolder = Mockito.mock(DeviceICookieHolder::class.java)
    lateinit var story: TvStory
    private var bufferForPlaybackMs = 500

    @Before
    fun setUp() {
        story = Mockito.spy(TvStory(singleScreenSessionIdProvider, startupPlaceTracker, iCookieHolder))
        Mockito.doNothing().`when`(story).sendEvent(Mockito.any())
        channelId = "1"
        currentTime = startTime
        eventNum = 0
        story.onEvent(createEvent(Events.EVENT_ON_CHANNEL_SWITCHING))
    }

    @Test
    fun onChannelSwitching() {
        testLiveTvEvents(Events.EVENT_ON_CHANNEL_SWITCHING)
    }

    @Test
    fun onCheckPolicy() {
        testLiveTvEvents(Events.EVENT_ON_CHECK_POLICY)
    }
    @Test
    fun onReleaseTvView() {
        testLiveTvEvents(Events.EVENT_ON_RELEASE_TV_VIEW)
    }

    @Test
    fun onCreateTvService() {
        testInputTvEvents(Events.EVENT_ON_CREATE_TV_SERVICE)
    }

    @Test
    fun onCreateTvSession() {
        testInputTvEvents(Events.EVENT_ON_CREATE_SESSION)
    }

    @Test
    fun onCreateOverlay() {
        testInputTvEvents(Events.EVENT_ON_CREATE_OVERLAY)
    }

    @Test
    fun onReleasePlayer() {
        testInputTvEvents(Events.EVENT_ON_RELEASE_PLAYER)
    }

    @Test
    fun onPlayerReady() {
        testInputTvEvents(Events.EVENT_ON_PLAYER_READY)
    }

    @Test
    fun onLoadingStart() {
        testInputTvEvents(Events.EVENT_ON_LOADING_START)
    }

    @Test
    fun onLoadingFinished() {
        testInputTvEvents(Events.EVENT_ON_LOADING_FINISHED)
    }

    @Test
    fun onFirstFrame() {
        testInputTvEvents(Events.EVENT_ON_FIRST_FRAME)
    }

    @Test
    fun onVideoAvailable() {
        story.onEvent(createEvent(Events.EVENT_ON_VIDEO_AVAILABLE))
        val expectedEvent = "{\"total_timespent_ms\":100,\"timespent_ms\":100,\"from\":\"tv-app\",\"channel_id\":\"$channelId\",\"event_time\":$currentTime}"
        val event = story.composeEventJson(story.event).toString()
        assertEquals(expectedEvent, event)
    }

    private fun testLiveTvEvents(nameEvent: Int) {
        story.onEvent(createEvent(nameEvent))
        val expectedEvent = "{\"total_timespent_ms\":100,\"timespent_ms\":100,\"from\":\"tv-app\",\"channel_id\":\"$channelId\",\"event_time\":$currentTime}"
        val event = story.composeEventJson(story.event).toString()
        assertEquals(expectedEvent, event)
    }

    private fun testInputTvEvents(nameEvent: Int) {
        story.onEvent(createEvent(nameEvent))
        val expectedEvent = "{\"total_timespent_ms\":${currentTime - startTime},\"timespent_ms\":100,\"from\":\"$fromInputServiceApp\",\"channel_id\":\"$channelId\",\"event_time\":$currentTime}"
        val event = story.composeEventJson(story.event).toString()
        assertEquals(expectedEvent, event)
    }

    @Test
    fun onCreatePlayer() {
        story.onEvent(createEvent(Events.EVENT_ON_CREATE_PLAYER))
        val expectedEvent = "{\"total_timespent_ms\":100,\"timespent_ms\":100,\"session_id\":\"$sessionId\",\"buffer_for_playback_ms\":$bufferForPlaybackMs,\"from\":\"input-service-app\",\"channel_id\":\"$channelId\",\"event_time\":$currentTime}"
        val event = (story.composeEventJson(story.event)).toString()
        assertEquals(expectedEvent, event)
    }

    private fun createEvent(event: Int): StoryEvent {
        val bundle = Bundle()
        when (event) {
            Events.EVENT_ON_CHANNEL_SWITCHING,
            Events.EVENT_ON_CHECK_POLICY,
            Events.EVENT_ON_RELEASE_TV_VIEW -> bundle.apply {
                putString(Keys.KEY_EVENT_FROM_APP, fromTvApp)
                putString(Keys.KEY_TV_CHANNEL_ID, channelId)
                putLong(Keys.KEY_TIMESTAMP, getNextTime())
            }
            Events.EVENT_ON_VIDEO_AVAILABLE  -> bundle.apply {
                putString(Keys.KEY_DEVICE_ID, deviceId)
                putString(Keys.KEY_EVENT_FROM_APP, fromTvApp)
                putString(Keys.KEY_TV_CHANNEL_ID, channelId)
                putLong(Keys.KEY_TIMESTAMP, getNextTime())
            }
            Events.EVENT_ON_CREATE_TV_SERVICE,
            Events.EVENT_ON_CREATE_SESSION,
            Events.EVENT_ON_CREATE_OVERLAY,
            Events.EVENT_ON_RELEASE_PLAYER,
            Events.EVENT_ON_LOADING_START,
            Events.EVENT_ON_PLAYER_READY,
            Events.EVENT_ON_FIRST_FRAME,
            Events.EVENT_ON_LOADING_FINISHED -> {
                bundle.apply {
                    putString(Keys.KEY_EVENT_FROM_APP, fromInputServiceApp)
                    putString(Keys.KEY_TV_CHANNEL_ID, channelId)
                    putLong(Keys.KEY_TIMESTAMP, getNextTime())
                }
            }
            Events.EVENT_ON_CREATE_PLAYER -> {
                bundle.apply {
                    putString(Keys.KEY_EVENT_FROM_APP, fromInputServiceApp)
                    putLong(Keys.KEY_TIMESTAMP, getNextTime())
                    putString(Keys.KEY_DEVICE_ID, deviceId)
                    putString(Keys.KEY_TV_CHANNEL_ID, channelId)
                    putString(Keys.KEY_PLAYER_SESSION_ID, sessionId)
                    putInt(Keys.KEY_BUFFER_FOR_PLAYBACK_MS, bufferForPlaybackMs)
                }
            }
        }
        return StoryEvent(event, bundle)
    }

    private fun getNextTime(): Long {
        currentTime += 100L * eventNum
        eventNum++
        return currentTime
    }
}
