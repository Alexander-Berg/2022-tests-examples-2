package ru.yandex.quasar.app.video.skippable

import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.fakes.FakeExecutorService
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.fakes.FakeResources
import ru.yandex.quasar.fakes.FakeScheduledFuture
import ru.yandex.quasar.protobuf.ModelObjects.SkippableFragments
import ru.yandex.quasar.protobuf.ModelObjects.SkippableFragments.Type.*
import ru.yandex.quasar.shadows.ShadowThreadUtil
import java.util.concurrent.TimeUnit
import kotlin.random.Random

@RunWith(RobolectricTestRunner::class)
@Config(
    shadows = [ShadowThreadUtil::class],
    instrumentedPackages = ["ru.yandex.quasar.concurrency"]
)
class SkippableSuggestManagerTest {
    private val fakeExecutor = FakeExecutorService()
    private val fakeResources = FakeResources()
    private val fakeMetricaReporter = FakeMetricaReporter()

    private val getPlayerPosition = { playerCurrentPosition }

    private val showSuggest = { _: String ->
        suggestShown = true
        suggestHidden = false
    }
    private val hideSuggest = {
        suggestHidden = true
        suggestShown = false
    }

    private var playerCurrentPosition = TimeUnit.SECONDS.toMillis(0)
    private var skippableSuggestTime = 15L
    private var suggestShown = false
    private var suggestHidden = false

    private fun createManager(fragments: List<SkippableFragments>): SkippableSuggestManager {
        return SkippableSuggestManager(
            fragments,
            getPlayerPosition,
            showSuggest,
            hideSuggest,
            fakeExecutor,
            fakeMetricaReporter,
            fakeResources,
            skippableSuggestTime
        )
    }

    @Test
    fun given_emptyList_when_createManager_then_eventsIsEmpty() {
        val manager = createManager(listOf())
        assert(manager.skippableFragments.isEmpty())
    }

    @Test
    fun given_fragmentFieldsAreMissing_when_createManager_then_eventsIsEmpty() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.getDefaultInstance(),
            SkippableFragments.newBuilder().setEndTimeSec(5).setType(OTHER).build(),
            SkippableFragments.newBuilder().setStartTimeSec(5).setType(OTHER).build(),
            SkippableFragments.newBuilder().setStartTimeSec(5).setEndTimeSec(6).build()
        )

        val manager = createManager(fragments)

        assert(manager.skippableFragments.isEmpty())
    }

    @Test
    fun given_startTimeIsGreaterThanEndTime_when_createManager_then_eventsIsEmpty() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(5).setEndTimeSec(1).setType(OTHER).build(),
            SkippableFragments.newBuilder().setStartTimeSec(5).setEndTimeSec(5).setType(OTHER).build()
        )

        val manager = createManager(fragments)

        assert(manager.skippableFragments.isEmpty())
    }

    @Test
    fun given_startTimeOrEndTimeIsNegative_when_createManager_then_eventsIsEmpty() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(-5).setEndTimeSec(-5).setType(OTHER).build(),
            SkippableFragments.newBuilder().setStartTimeSec(-5).setEndTimeSec(5).setType(OTHER).build(),
            SkippableFragments.newBuilder().setStartTimeSec(5).setEndTimeSec(-5).setType(OTHER).build()
        )

        val manager = createManager(fragments)

        assert(manager.skippableFragments.isEmpty())
    }

    @Test
    fun given_notSortedFragments_when_createManager_then_eventsSorted() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(100).setEndTimeSec(110).setType(INTRO).build(),
            SkippableFragments.newBuilder().setStartTimeSec(5).setEndTimeSec(15).setType(CREDITS).build(),
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(RECAP).build(),
            SkippableFragments.newBuilder().setStartTimeSec(55).setEndTimeSec(75).setType(NEXT_EPISODE).build(),
            SkippableFragments.newBuilder().setStartTimeSec(0).setEndTimeSec(5).setType(OTHER).build()
        )
        val sortedFragments = fragments.sortedBy { t -> t.startTimeSec }

        val manager = createManager(fragments)

        assertEquals(manager.skippableFragments.size, sortedFragments.size)
        for (i in fragments.indices) {
            assertEquals(sortedFragments[i].type, manager.skippableFragments[i].type)
            assertEquals(sortedFragments[i].startTimeSec, manager.skippableFragments[i].startTimeSec)
            assertEquals(sortedFragments[i].endTimeSec, manager.skippableFragments[i].endTimeSec)
        }
    }

    @Test
    fun given_emptyList_when_startManager_then_checkIsNotScheduled() {
        createManager(listOf())
        assertEquals(0, fakeExecutor.items.size)
    }

    @Test
    fun given_notEmptyList_when_startManager_then_checkIsScheduled() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(25).setEndTimeSec(40).setType(OTHER).build()
        )

        createManager(fragments)

        assertEquals(1, fakeExecutor.items.size)
    }

    @Test
    fun given_fragmentsList_when_changeCurrentPosition_then_newCheckHasBeenScheduled() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(OTHER).build()
        )
        val manager = createManager(fragments)
        val firstCheck = fakeExecutor.items.values.first().future as FakeScheduledFuture
        fakeExecutor.items.clear()

        playerCurrentPosition = TimeUnit.SECONDS.toMillis(25)
        manager.onCurrentPositionChanged()

        assertEquals(1, fakeExecutor.items.size)
        // previous check has to be cancelled
        assert(firstCheck.isCancelled)
    }

    @Test
    fun given_fragmentsList_when_enterFragment_then_suggestShown() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(35)

        createManager(fragments)

        assert(suggestShown)
    }

    @Test
    fun given_fragmentsShown_when_exitFragment_then_suggestHidden() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(30)
        createManager(fragments)

        // exit fragment
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(40)
        fakeExecutor.runAllJobs()

        assert(suggestHidden)
    }

    @Test
    fun given_longFragmentShown_when_15secPass_then_suggestHidden() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(100).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(30)
        createManager(fragments)

        // exit fragment
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(30L + skippableSuggestTime)
        fakeExecutor.runAllJobs()

        assert(suggestHidden)
    }

    @Test
    fun given_fragment_when_changePositionAndRunScheduledChecking_then_waitTimeBeforeShowSuggestChanged() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(100).setEndTimeSec(150).setType(OTHER).build()
        )
        createManager(fragments)

        for (i in 1..10) {
            playerCurrentPosition = TimeUnit.SECONDS.toMillis(Random.nextLong(0, 99))
            fakeExecutor.runAllJobs()
            assertEquals(1, fakeExecutor.items.size)
            val future = fakeExecutor.items.values.first().future as FakeScheduledFuture
            assertEquals(TimeUnit.SECONDS.toMillis(100L) - playerCurrentPosition, future.delay)
        }
    }

    @Test
    fun given_fragment_when_changeCurrentPositionAndRunScheduledChecking_then_waitTimeBeforeHideSuggestChanged() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(100).setEndTimeSec(200).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(100)
        createManager(fragments)

        for (i in 1..10) {
            playerCurrentPosition = TimeUnit.SECONDS.toMillis(100L + i)
            fakeExecutor.runAllJobs()
            assertEquals(1, fakeExecutor.items.size)
            val future = fakeExecutor.items.values.first().future as FakeScheduledFuture
            assertEquals(
                TimeUnit.SECONDS.toMillis(skippableSuggestTime - i),
                future.delay
            )
        }
    }

    @Test
    fun given_longFragment_when_changeCurrentPosition_then_wait15secBeforeHide() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(100).setEndTimeSec(200).setType(OTHER).build()
        )
        val manager = createManager(fragments)

        for (i in 1..10) {
            fakeExecutor.items.clear()
            playerCurrentPosition = TimeUnit.SECONDS.toMillis(
                Random.nextLong(
                    100,
                    200 - skippableSuggestTime - SkippableSuggestManager.HIDE_BEFORE_END_SEC
                )
            )
            manager.onCurrentPositionChanged()
            assertEquals(1, fakeExecutor.items.size)
            val future = fakeExecutor.items.values.first().future as FakeScheduledFuture
            assertEquals(
                TimeUnit.SECONDS.toMillis(skippableSuggestTime),
                future.delay
            )
        }
    }

    @Test
    fun given_shortFragment_when_changeCurrentPositionRunScheduledChecking_then_waitFragmentEnds() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(100).setEndTimeSec(115).setType(OTHER).build()
        )
        createManager(fragments)

        for (i in 1..10) {
            playerCurrentPosition = TimeUnit.SECONDS.toMillis(100L + i)
            fakeExecutor.runAllJobs()
            assertEquals(1, fakeExecutor.items.size)
            val future = fakeExecutor.items.values.first().future as FakeScheduledFuture
            assertEquals(
                TimeUnit.SECONDS.toMillis(115L - SkippableSuggestManager.HIDE_BEFORE_END_SEC) - playerCurrentPosition,
                future.delay
            )
        }
    }

    @Test
    fun given_shownFragment_when_changeCurrentPositionRunScheduledChecking_then_fragmentIsNotHidden() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(100).setEndTimeSec(115).setType(OTHER).build(),
            SkippableFragments.newBuilder().setStartTimeSec(200).setEndTimeSec(215).setType(OTHER).build()
        )
        createManager(fragments)

        for (i in 1..10) {
            playerCurrentPosition = TimeUnit.SECONDS.toMillis(100L + i)
            fakeExecutor.runAllJobs()
            assert(!suggestHidden)
        }
    }

    @Test
    fun given_hiddenFragment_when_changeCurrentPositionAndRunScheduledChecking_then_fragmentIsNotShown() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(100).setEndTimeSec(150).setType(OTHER).build(),
            SkippableFragments.newBuilder().setStartTimeSec(200).setEndTimeSec(215).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(100)
        createManager(fragments)
        // hide fragment
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(100L + skippableSuggestTime)
        fakeExecutor.runAllJobs()

        for (i in 1..10) {
            playerCurrentPosition = TimeUnit.SECONDS.toMillis(100L + skippableSuggestTime + i)
            fakeExecutor.runAllJobs()
            assert(!suggestShown)
        }
    }

    @Test
    fun given_fragment_when_oneSecondLeft_then_scheduleMinimumDelay() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(100).setEndTimeSec(115).setType(OTHER).build()
        )
        createManager(fragments)

        playerCurrentPosition = TimeUnit.SECONDS.toMillis(99) + 450
        fakeExecutor.runAllJobs()

        assertEquals(1, fakeExecutor.items.size)
        val future = fakeExecutor.items.values.first().future as FakeScheduledFuture
        assertEquals(TimeUnit.SECONDS.toMillis(100) - playerCurrentPosition, future.delay)
    }

    @Test
    fun given_consecutiveFragments_when_runAllJobs_then_fragmentIsNotHidden() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(OTHER).build(),
            SkippableFragments.newBuilder().setStartTimeSec(40).setEndTimeSec(50).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(30)
        createManager(fragments)

        // exit fragment
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(40)
        fakeExecutor.runAllJobs()

        assert(!suggestHidden)
        assert(suggestShown)
    }

    @Test
    fun given_shownFragment_when_changeCurrentPosition_then_stateIsDropped() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(30)
        val manager = createManager(fragments)
        val future = fakeExecutor.items.values.first().future as FakeScheduledFuture

        playerCurrentPosition = TimeUnit.SECONDS.toMillis(0)
        manager.onCurrentPositionChanged()

        assert(future.isCancelled)
        assert(suggestHidden)
    }

    @Test
    fun given_shownFragment_when_pause_then_stateIsNotDropped() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(30)
        val manager = createManager(fragments)
        val future = fakeExecutor.items.values.first().future as FakeScheduledFuture

        manager.pause()

        assert(!suggestHidden)
        assert(future.isCancelled)
    }

    @Test
    fun given_shownFragment_when_resume_then_newCheckHasBeenScheduled() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(30)
        val manager = createManager(fragments)
        val firstCheck = fakeExecutor.items.values.first().future as FakeScheduledFuture
        fakeExecutor.items.clear()

        manager.pause()
        manager.resume()

        assert(!suggestHidden)
        assert(firstCheck.isCancelled)
        assertEquals(1, fakeExecutor.items.size)
    }

    @Test
    fun given_shownFragment_when_destroy_then_stateIsDropped() {
        val fragments = listOf<SkippableFragments>(
            SkippableFragments.newBuilder().setStartTimeSec(30).setEndTimeSec(40).setType(OTHER).build()
        )
        playerCurrentPosition = TimeUnit.SECONDS.toMillis(30)
        val manager = createManager(fragments)
        val future = fakeExecutor.items.values.first().future as FakeScheduledFuture

        manager.destroy()

        assert(future.isCancelled)
        assert(suggestHidden)
    }
}
