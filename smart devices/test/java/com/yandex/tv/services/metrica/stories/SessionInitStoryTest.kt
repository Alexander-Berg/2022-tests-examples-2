package com.yandex.tv.services.metrica.stories

import android.content.Context
import android.content.pm.PackageInfo
import android.os.Handler
import android.os.Looper
import androidx.test.core.app.ApplicationProvider
import androidx.work.OneTimeWorkRequest
import com.yandex.tv.services.common.ServiceFuture
import com.yandex.tv.services.experiments.ExperimentsHelper
import com.yandex.tv.services.experiments.ExperimentsServiceSdk2
import com.yandex.tv.services.metrica.CommonMetricaFacade
import com.yandex.tv.services.metrica.Events
import com.yandex.tv.services.metrica.IMetricaCommon
import com.yandex.tv.services.metrica.Keys
import com.yandex.tv.services.metrica.StoryEvent
import com.yandex.tv.services.metrica.stories.util.SessionIdProvider
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.emptyOrNullString
import org.hamcrest.Matchers.not
import org.hamcrest.core.IsEqual.equalTo
import org.json.JSONObject
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.atLeast
import org.mockito.kotlin.doNothing
import org.mockito.kotlin.doReturn
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.spy
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import java.util.concurrent.TimeUnit

@RunWith(RobolectricTestRunner::class)
class SessionInitStoryTest {

    private var story: SessionInitStory = mock()
    private var experimentsHelper: ExperimentsHelper = mock()

    private var serverLogData: String? = JSONObject().apply {
        put("data", "log data")
    }.toString()

    private val serverLogDataFuture = object: ServiceFuture<String> {
        override fun cancel(mayInterruptIfRunning: Boolean) = true

        override fun isCancelled() = false

        override fun isDone() = true

        override fun get() = serverLogData

        override fun get(timeout: Long, unit: TimeUnit?) = serverLogData

        override fun getSafely() = serverLogData

        override fun getSafely(timeout: Long, unit: TimeUnit) = serverLogData

        override fun getSafely(defaultValue: String?) = serverLogData

        override fun getSafely(timeout: Long, unit: TimeUnit, defaultValue: String?) = serverLogData

        override fun setCallbacks(
            onSuccess: ServiceFuture.Consumer<String>,
            onError: ServiceFuture.Consumer<Throwable>
        ) = true
    }

    private val metricaImpl: IMetricaCommon = mock()

    private val sessionIdProvider: SessionIdProvider = mock()

    @Before
    fun setUp() {
        val context: Context = ApplicationProvider.getApplicationContext()
        val experimentsServiceMock: ExperimentsServiceSdk2 = mock {
            on { serverLogData } doReturn serverLogDataFuture
        }

        experimentsHelper = mock {
            on { testBuckets } doReturn "1000,0,0;2000,0,85"
            on { overrideTestIds } doReturn "1000,2000"
            on { effectiveTestIds } doReturn "1000,2000"
        }

        story = spy(SessionInitStory(context, Handler(Looper.getMainLooper()), mock(), sessionIdProvider, experimentsHelper))

        doReturn(emptyList<PackageInfo>()).whenever(story).getInstalledPackages(any())
        doNothing().whenever(story).schedule(any())
        doNothing().whenever(story).cancelScheduled()
        doReturn(experimentsServiceMock).whenever(story).createExperimentsService()

        CommonMetricaFacade.setImpl(metricaImpl)
    }

    @Test
    fun `should send session_init and experiments on EVENT_SCREEN_ON`() {
        serverLogData = JSONObject().apply {
            put("data", "test log data")
        }.toString()
        story.onEvent(StoryEvent(Events.EVENT_SCREEN_ON, null))

        verify(story, times(1)).reportExperiments(any())
        verify(story, times(1)).reportSessionInit(any())
    }

    @Test
    fun `should send session_init on EVENT_SCREEN_ON with test ids and test buckets`() {
        serverLogData = JSONObject().apply {
            put("data", "log data")
        }.toString()
        story.onEvent(StoryEvent(Events.EVENT_SCREEN_ON, null))

        val captor = argumentCaptor<JSONObject>()

        verify(story, times(1)).reportSessionInit(captor.capture())

        val jsonEventValue = captor.firstValue

        assertThat(jsonEventValue.getString(Keys.KEY_TEST_IDS), not(emptyOrNullString()))
        assertThat(jsonEventValue.getString(Keys.KEY_TEST_BUCKETS), not(emptyOrNullString()))
    }

    @Test
    fun `should send session_init on EVENT_SESSION_INIT with test ids and test buckets`() {
        serverLogData = JSONObject().apply {
            put("data", "log data")
        }.toString()
        story.onEvent(StoryEvent(Events.EVENT_SESSION_INIT, null))

        val captor = argumentCaptor<JSONObject>()

        verify(story, times(1)).reportSessionInit(captor.capture())

        val jsonEventValue = captor.firstValue

        assertThat(jsonEventValue.getString(Keys.KEY_TEST_IDS), not(emptyOrNullString()))
        assertThat(jsonEventValue.getString(Keys.KEY_TEST_BUCKETS), not(emptyOrNullString()))
    }

    @Test
    fun `should send experiments on EVENT_SCREEN_ON with exact log data`() {
        serverLogData = JSONObject().apply {
            put("data", "test log data")
        }.toString()
        story.onEvent(StoryEvent(Events.EVENT_SCREEN_ON, null))

        val captor = argumentCaptor<String>()

        verify(story, times(1)).reportExperiments(captor.capture())

        assertThat(captor.firstValue, equalTo(serverLogData))
    }

    @Test
    fun `should send session_init and no experiments on EVENT_SCREEN_ON and no logData`() {
        serverLogData = null
        story.onEvent(StoryEvent(Events.EVENT_SCREEN_ON, null))

        verify(story, times(0)).reportExperiments(any())
        verify(story, times(1)).reportSessionInit(any())
    }

    @Test
    fun `should send session_init and no experiments on EVENT_SCREEN_ON and not json logData`() {
        serverLogData = "simple string"
        story.onEvent(StoryEvent(Events.EVENT_SCREEN_ON, null))

        verify(metricaImpl, times(0)).sendJson(eq(SessionInitStory.METRICA_EVENT_EXPERIMENTS), any(), any())
        verify(story, times(1)).reportSessionInit(any())
    }

    @Test
    fun `should schedule session_init from EVENT_SCREEN_ON`() {
        serverLogData = JSONObject().apply {
            put("data", "test log data")
        }.toString()
        story.onEvent(StoryEvent(Events.EVENT_SCREEN_ON, null))

        val captor = argumentCaptor<OneTimeWorkRequest>()

        verify(story, times(1)).cancelScheduled()
        verify(story, times(1)).schedule(captor.capture())

        assertThat(captor.firstValue.workSpec.initialDelay, equalTo(TimeUnit.HOURS.toMillis(12)))
    }

    @Test
    fun `should put session_id environment session_init from EVENT_SCREEN_ON`() {
        serverLogData = JSONObject().apply {
            put("data", "test log data")
        }.toString()

        doReturn("session_id").whenever(sessionIdProvider).getSessionId()

        story.onEvent(StoryEvent(Events.EVENT_SCREEN_ON, null))

        val nameCaptor = argumentCaptor<String>()
        val valueCaptor = argumentCaptor<String>()
        val permanentCaptor = argumentCaptor<Boolean>()

        verify(metricaImpl, atLeast(1)).putEnvironmentValue(
            nameCaptor.capture(),
            valueCaptor.capture(),
            permanentCaptor.capture()
        )

        assertThat(nameCaptor.firstValue, equalTo(CommonMetricaFacade.ENVIRONMENT_SESSION_ID))
        assertThat(valueCaptor.firstValue, not(emptyOrNullString()))
        assertThat(permanentCaptor.firstValue, equalTo(true))
    }
}
