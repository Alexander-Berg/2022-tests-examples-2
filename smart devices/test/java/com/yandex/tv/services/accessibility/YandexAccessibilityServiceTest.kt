package com.yandex.tv.services.accessibility

import android.accessibilityservice.AccessibilityServiceInfo
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import com.yandex.tv.common.di.NetworkComponent
import com.yandex.tv.services.metrica.Events
import com.yandex.tv.services.metrica.Keys
import com.yandex.tv.services.metrica.MetricaServiceSdk2
import org.hamcrest.CoreMatchers.equalTo
import org.hamcrest.MatcherAssert.assertThat
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.any
import org.mockito.Mockito.eq
import org.mockito.Mockito.mock
import org.mockito.Mockito.never
import org.mockito.Mockito.spy
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowLooper
import java.util.concurrent.TimeUnit

@RunWith(RobolectricTestRunner::class)
@Config(manifest = Config.NONE)
class YandexAccessibilityServiceTest {

    private val mockMetricaSdk = mock(MetricaServiceSdk2::class.java)
    private var accessibilityService: YandexAccessibilityService? = null

    @Before
    fun setup() {
        AccessibilityComponent.instance = AccessibilityComponent(
            mock(NetworkComponent::class.java).also {
                whenever(it.metricaSdk).doReturn(mockMetricaSdk)
            },
            object : AccessibilityConfig {
                override val accessibilityServiceEnabled: Boolean
                    get() = true
                override val accessibilityNotificationTimeoutMs: Long
                    get() = 100
                override val accessibilityPackages: List<String>
                    get() = listOf("com.yandex.tv.home")
                override val unresponsiveUiTimeoutMs: Long
                    get() = 2000

                override fun addAccessibilityConfigListener(listener: AccessibilityConfigListener) {
                    //noop
                }
            }
        )
        accessibilityService = spy(YandexAccessibilityService()).also {
            whenever(it.serviceInfo).doReturn(AccessibilityServiceInfo())
        }
        accessibilityService!!.onServiceConnected()
    }

    @After
    fun tearDown() {
        accessibilityService!!.onInterrupt()
        accessibilityService = null
    }

    @Test
    fun `click, idle for 3 seconds - unresponsive_ui event sent`() {
        accessibilityService!!.onAccessibilityEvent(CLICK)
        ShadowLooper.idleMainLooper(3, TimeUnit.SECONDS)
        val eventCaptor = argumentCaptor<Bundle>()
        verify(mockMetricaSdk, times(1)).processEvent(eq(Events.EVENT_RAW), eventCaptor.capture())
        assertThat(
            eventCaptor.firstValue.getString(Keys.KEY_EVENT_NAME),
            equalTo(YandexAccessibilityService.METRICA_EVENT_UI_UNRESPONSIVE)
        )
    }

    @Test
    fun `long click, idle for 3 seconds - unresponsive_ui event sent`() {
        accessibilityService!!.onAccessibilityEvent(LONG_CLICK)
        ShadowLooper.idleMainLooper(3, TimeUnit.SECONDS)
        val eventCaptor = argumentCaptor<Bundle>()
        verify(mockMetricaSdk, times(1)).processEvent(eq(Events.EVENT_RAW), eventCaptor.capture())
        assertThat(
            eventCaptor.firstValue.getString(Keys.KEY_EVENT_NAME),
            equalTo(YandexAccessibilityService.METRICA_EVENT_UI_UNRESPONSIVE)
        )
    }

    @Test
    fun `click, idle for 1 second - unresponsive_ui event not sent`() {
        accessibilityService!!.onAccessibilityEvent(CLICK)
        ShadowLooper.idleMainLooper(1, TimeUnit.SECONDS)
        verify(mockMetricaSdk, never()).processEvent(eq(Events.EVENT_RAW), any())
    }

    @Test
    fun `long click, idle for 1 second - unresponsive_ui event not sent`() {
        accessibilityService!!.onAccessibilityEvent(LONG_CLICK)
        ShadowLooper.idleMainLooper(1, TimeUnit.SECONDS)
        verify(mockMetricaSdk, never()).processEvent(eq(Events.EVENT_RAW), any())
    }

    @Test
    fun `click, idle for 1 second, interrupt - unresponsive_ui event not sent`() {
        accessibilityService!!.onAccessibilityEvent(CLICK)
        ShadowLooper.idleMainLooper(1, TimeUnit.SECONDS)
        accessibilityService!!.onInterrupt()
        ShadowLooper.idleMainLooper(2, TimeUnit.SECONDS)
        verify(mockMetricaSdk, never()).processEvent(eq(Events.EVENT_RAW), any())
    }

    @Test
    fun `click, idle for 1 second, window content changed - unresponsive_ui event not sent`() {
        accessibilityService!!.onAccessibilityEvent(CLICK)
        ShadowLooper.idleMainLooper(1, TimeUnit.SECONDS)
        accessibilityService!!.onAccessibilityEvent(WINDOW_CONTENT_CHANGED)
        ShadowLooper.idleMainLooper(2, TimeUnit.SECONDS)
        verify(mockMetricaSdk, never()).processEvent(eq(Events.EVENT_RAW), any())
    }

    @Test
    fun `click, idle for 1 second, window state changed - unresponsive_ui event not sent`() {
        accessibilityService!!.onAccessibilityEvent(CLICK)
        ShadowLooper.idleMainLooper(1, TimeUnit.SECONDS)
        accessibilityService!!.onAccessibilityEvent(WINDOW_STATE_CHANGED)
        ShadowLooper.idleMainLooper(2, TimeUnit.SECONDS)
        verify(mockMetricaSdk, never()).processEvent(eq(Events.EVENT_RAW), any())
    }

    @Test
    fun `click, idle for 1 second, windows changed - unresponsive_ui event not sent`() {
        accessibilityService!!.onAccessibilityEvent(CLICK)
        ShadowLooper.idleMainLooper(1, TimeUnit.SECONDS)
        accessibilityService!!.onAccessibilityEvent(WINDOWS_CHANGED)
        ShadowLooper.idleMainLooper(2, TimeUnit.SECONDS)
        verify(mockMetricaSdk, never()).processEvent(eq(Events.EVENT_RAW), any())
    }

    companion object {
        private val CLICK = AccessibilityEvent()
        private val LONG_CLICK = AccessibilityEvent()
        private val WINDOW_CONTENT_CHANGED = AccessibilityEvent()
        private val WINDOW_STATE_CHANGED = AccessibilityEvent()
        private val WINDOWS_CHANGED = AccessibilityEvent()

        init {
            //Robolectric doesn't have constructor AccessibilityEvent(eventType)
            CLICK.eventType = AccessibilityEvent.TYPE_VIEW_CLICKED
            LONG_CLICK.eventType = AccessibilityEvent.TYPE_VIEW_LONG_CLICKED
            WINDOW_CONTENT_CHANGED.eventType = AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED
            WINDOW_STATE_CHANGED.eventType = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
            WINDOWS_CHANGED.eventType = AccessibilityEvent.TYPE_WINDOWS_CHANGED
        }
    }
}
