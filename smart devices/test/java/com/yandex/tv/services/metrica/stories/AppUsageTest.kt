package com.yandex.tv.services.metrica.stories

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.yandex.tv.services.metrica.stories.usage.AppUsageMetricaGatherer
import com.yandex.tv.services.metrica.stories.usage.AppUsageUtils
import com.yandex.tv.services.metrica.stories.usage.models.AppInteractionStat
import com.yandex.tv.services.metrica.stories.usage.models.LifecycleState
import org.hamcrest.CoreMatchers.equalTo
import org.hamcrest.MatcherAssert.assertThat
import org.json.JSONObject
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.anyInt
import org.mockito.MockedStatic
import org.mockito.Mockito
import org.mockito.kotlin.spy
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowLog

@RunWith(RobolectricTestRunner::class)
@Config(manifest=Config.NONE)
class AppUsageTest {

    private lateinit var gatherer: AppUsageMetricaGatherer

    @Before
    fun setUp() {
        ShadowLog.stream = System.out

        val context: Context = ApplicationProvider.getApplicationContext()
        gatherer = spy(AppUsageMetricaGatherer(context))

        mockedUtils = Mockito.mockStatic(AppUsageUtils::class.java).apply {
            `when`<Long> { AppUsageUtils.dayIndexToTheEndOfDayMs(anyInt()) }.thenAnswer { answer ->
                val idx = answer.arguments[0] as Int
                return@thenAnswer (idx + 1) * pseudoTimeDayLength
            }
            `when`<Long> { AppUsageUtils.dayIndexToTsMs(anyInt()) }.thenAnswer { answer ->
                val idx = answer.arguments[0] as Int
                return@thenAnswer idx * pseudoTimeDayLength
            }
        }
    }

    @After
    fun tearDown() {
        mockedUtils?.close()
    }

    @Test
    fun `statistics for one day`() {
        val stats = gatherer.gatherStats(mapOf(0 to day1Events), day1Start, day1End)
        stats.forEach {
            assertThat(it.toString(), equalTo(day1Json.toString()))
        }
    }

    @Test
    fun `statistics for 3 days`() {
        val stats = gatherer.gatherStats(
            mapOf(
                0 to day1Events,
                1 to day2Events,
                2 to day3Events
            ),
            day1Start,
            day3End
        )
        val jsons = listOf(day1Json, day2Json, day3JsonFull)
        stats.forEachIndexed { idx, it ->
            assertThat(it.toString(), equalTo(jsons[idx].toString()))
        }
    }

    @Test
    fun `statistics for 2,5 days`() {
        val stats = gatherer.gatherStats(
            mapOf(
                0 to day1Events,
                1 to day2Events,
                2 to day3HalfEvents
            ),
            day1Start,
            day3Half.toLong()
        )
        val jsons = listOf(day1Json, day2Json, day3JsonHalf)
        stats.forEachIndexed { idx, it ->
            assertThat(it.toString(), equalTo(jsons[idx].toString()))
        }
    }

    @Test
    fun `statistics for 1,5-2,5 days`() {
        val stats = gatherer.gatherStats(
            mapOf(
                1 to day2HalfEvents,
                2 to day3HalfEvents
            ),
            day2Half.toLong(),
            day3Half.toLong()
        )
        val jsons = listOf(day2HalfJson, day3JsonHalf)
        stats.forEachIndexed { idx, it ->
            assertThat(it.toString(), equalTo(jsons[idx].toString()))
        }
    }

    @Test
    fun `no statistics for idling`() {
        val stats = gatherer.gatherStats(
            emptyMap(),
            day3Start,
            day3Half.toLong()
        )
        assertThat(stats.size, equalTo(0))
    }

    companion object {

        private var mockedUtils: MockedStatic<AppUsageUtils>? = null

        private val aMainActivity = "test.a/test.a.MainActivity"
        private val aAnotherActivity = "test.a/test.a.AnotherActivity"
        private val bMainActivity = "test.b/test.b.MainActivity"
        private val bAnotherActivity = "test.b/test.b.AnotherActivity"

        //use pseudo time for events and requests
        private val pseudoTimeDayLength = 24000L

        //day1: aMainActivity -> aAnotherActivity -> bAnotherActivity -> aMainActivity
        private val day1Start = 0L
        private val day1End = pseudoTimeDayLength
        private val day1Events = listOf(
                    AppInteractionStat(aMainActivity, LifecycleState.RESUMED, 1000),
                    AppInteractionStat(aMainActivity, LifecycleState.PAUSED, 4000),
                    AppInteractionStat(aAnotherActivity, LifecycleState.RESUMED, 4000),
                    AppInteractionStat(bAnotherActivity, LifecycleState.RESUMED, 8000),
                    AppInteractionStat(aAnotherActivity, LifecycleState.PAUSED, 8000),
                    AppInteractionStat(bAnotherActivity, LifecycleState.PAUSED, 15000),
                    AppInteractionStat(aMainActivity, LifecycleState.RESUMED, 15000),
        )
        private val day1Json = JSONObject("""{
            "timestamp": ${day1End},
            "apps": {
                "test.a/test.a.MainActivity" : 12,
                "test.a/test.a.AnotherActivity" : 4,
                "test.b/test.b.AnotherActivity" : 7
            }
        }""".trimIndent())

        //day2: aMainActivity -> aAnotherActivity -> bAnotherActivity -> bMainActivity
        private val day2Start = pseudoTimeDayLength
        private val day2End = pseudoTimeDayLength * 2
        private val day2Half = pseudoTimeDayLength * 1.5
        private val day2Events = listOf(
                AppInteractionStat(aMainActivity, LifecycleState.RESUMED, 24000),
                AppInteractionStat(aMainActivity, LifecycleState.PAUSED, 34000),
                AppInteractionStat(aAnotherActivity, LifecycleState.RESUMED, 34000),
                AppInteractionStat(bAnotherActivity, LifecycleState.RESUMED, 35000),
                AppInteractionStat(aAnotherActivity, LifecycleState.PAUSED, 35000),
                AppInteractionStat(bAnotherActivity, LifecycleState.PAUSED, 39000),
                AppInteractionStat(bMainActivity, LifecycleState.RESUMED, 39000),
        )
        private val day2Json = JSONObject("""{
            "timestamp": ${day2End},
            "apps": {
                "test.a/test.a.MainActivity" : 10,
                "test.a/test.a.AnotherActivity" : 1,
                "test.b/test.b.AnotherActivity" : 4,
                "test.b/test.b.MainActivity" : 9
            }
        }""".trimIndent())
        private val day2HalfEvents = listOf(
            AppInteractionStat(bAnotherActivity, LifecycleState.PAUSED, 39000),
            AppInteractionStat(bMainActivity, LifecycleState.RESUMED, 39000),
        )
        private val day2HalfJson = JSONObject("""{
            "timestamp": ${day2End},
            "apps": {
                "test.b/test.b.AnotherActivity" : 3,
                "test.b/test.b.MainActivity" : 9
            }
        }""".trimIndent())

        //day3: bMainActivity -> aMainActivity -> aAnotherActivity -> bAnotherActivity -> bMainActivity
        private val day3Start = pseudoTimeDayLength * 2
        private val day3Half = pseudoTimeDayLength * 2.5
        private val day3End = pseudoTimeDayLength * 3
        private val day3Events = listOf(
                AppInteractionStat(bMainActivity, LifecycleState.PAUSED, 50000),
                AppInteractionStat(aMainActivity, LifecycleState.RESUMED, 50000),
                AppInteractionStat(aMainActivity, LifecycleState.PAUSED, 55000),
                AppInteractionStat(aAnotherActivity, LifecycleState.RESUMED, 55000),
                AppInteractionStat(bAnotherActivity, LifecycleState.RESUMED, 60000),
                AppInteractionStat(aAnotherActivity, LifecycleState.PAUSED, 60000),
                AppInteractionStat(bAnotherActivity, LifecycleState.PAUSED, 66000),
                AppInteractionStat(bMainActivity, LifecycleState.RESUMED, 66000),
        )
        private val day3JsonFull = JSONObject("""{
            "timestamp": ${day3End},
            "apps": {
                "test.b/test.b.MainActivity" : 8,
                "test.a/test.a.MainActivity" : 5,
                "test.a/test.a.AnotherActivity" : 5,
                "test.b/test.b.AnotherActivity" : 6
            }
        }""".trimIndent())
        private val day3HalfEvents = listOf(
            AppInteractionStat(bMainActivity, LifecycleState.PAUSED, 50000),
            AppInteractionStat(aMainActivity, LifecycleState.RESUMED, 50000),
            AppInteractionStat(aMainActivity, LifecycleState.PAUSED, 55000),
            AppInteractionStat(aAnotherActivity, LifecycleState.RESUMED, 55000),
            AppInteractionStat(aAnotherActivity, LifecycleState.PAUSED, 60000)
        )
        private val day3JsonHalf = JSONObject("""{
            "timestamp": ${day3End},
            "apps": {
                "test.b/test.b.MainActivity" : 2,
                "test.a/test.a.MainActivity" : 5,
                "test.a/test.a.AnotherActivity" : 5
            }
        }""".trimIndent())
    }
}
