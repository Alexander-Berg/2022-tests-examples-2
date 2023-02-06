package ru.yandex.quasar.centaur_app.stack

import kotlinx.coroutines.flow.Flow
import java.util.UUID
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runBlockingTest
import org.junit.Before
import org.junit.Ignore
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseCoroutinesUnitTest
import ru.yandex.quasar.centaur_app.FakeMetricaReporter
import ru.yandex.quasar.centaur_app.action_space.ActionSpaceIdHandler
import ru.yandex.quasar.centaur_app.initialization.splash.SplashFragment
import ru.yandex.quasar.centaur_app.stack.contract.Layer
import ru.yandex.quasar.centaur_app.stack.contract.LayerContents
import ru.yandex.quasar.centaur_app.stack.contract.LayerInfo
import ru.yandex.quasar.centaur_app.stack.contract.LayerManager
import ru.yandex.quasar.centaur_app.stack.fragments.ActionSpaceIdResolver
import ru.yandex.quasar.centaur_app.stack.fragments.FragmentsController
import ru.yandex.quasar.centaur_app.stack.fragments.FragmentsControllerSpy
import ru.yandex.quasar.centaur_app.stack.fragments.RestorationData
import ru.yandex.quasar.centaur_app.stack.item.LayerItemComposition
import ru.yandex.quasar.centaur_app.stack.item.lifetime.LifetimeCheckerFactory
import ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons.AliceStateReason
import ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons.AudioPlayerReason
import ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons.RawReason
import ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons.UserInteractionReason
import ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons.VideoCallReason
import ru.yandex.quasar.centaur_app.stack.item.lifetime.reasons.VideoPlayerReason
import ru.yandex.quasar.centaur_app.utils.BenchmarkTimer

@RunWith(RobolectricTestRunner::class)
class LayerManagerImplUnitTest: BaseCoroutinesUnitTest() {
    private val fragmentsController: FragmentsController = FragmentsControllerSpy(listOf())

    private lateinit var layerManager: LayerManager

    @Before
    override fun setup() {
        super.setup()
        layerManager = LayerManagerImpl(
            coroutineScope = coroutineScope,
            fragmentsController = fragmentsController,
            metricaReporter = FakeMetricaReporter(),
            actionSpaceIdHandler = ActionSpaceIdHandler {},
            actionSpaceIdResolver = ActionSpaceIdResolver { flowOf(null) },
            lifetimeCheckerFactory = LifetimeCheckerFactory(
                userInteractionReason = UserInteractionReason(
                    userInteractions = flowOf(),
                    coroutineScope = coroutineScope
                ),
                aliceStateReason = AliceStateReason(
                    aliceStateFlow = flowOf()
                ),
                audioPlayerReason = AudioPlayerReason(
                    audioPlayerThinEvents = flowOf()
                ),
                videoPlayerReason = VideoPlayerReason(
                    videoPlayerEvents = flowOf(),
                    coroutineScope = coroutineScope
                ),
                rawReason = RawReason(
                    isActive = flowOf()
                ),
                videoCallReason = VideoCallReason(
                  telegramCallStatusFlow = flowOf()
                ),
                coroutineScope = coroutineScope,
            ),
            useBackendInactivityTimeout = { true },
            useServerSideActivityKinds = { true }
        )
    }

    @Test
    fun `when layer states are different by content they should not be equal`() {
        val ls1 = LayerManagerImpl.LayerState(
            layer = Layer.ROOT,
            currentItem = FakeLayerItemComposition(
                content = LayerContents.Home,
                layer = Layer.ROOT,
                restorationData = null,
                id = UUID.randomUUID(),
                isExpired = flowOf(false)
            )
        )
        val ls2 = LayerManagerImpl.LayerState(
            layer = Layer.ROOT,
            currentItem = FakeLayerItemComposition(
                content = LayerContents.Home,
                layer = Layer.ROOT,
                restorationData = null,
                id = UUID.randomUUID(),
                isExpired = flowOf(false)
            )
        )
        assert(!ls1.equals(ls2))
    }

    @Test
    fun `when system started then current layer is null`() {
        runBlockingTest {
            testDispatcher.advanceUntilIdle()
            assert(layerManager.highestLayer.first() == null)
        }
    }

    @Test
    fun `when show new layer on order then it becomes top`() {
        runBlockingTest {
            var stack = ArrayList<Layer>()
            for (layer in Layer.list(false)) {
                stack.add(layer)

                val dummy = makeDummyLayerInfo()
                layerManager.show(layer, dummy)
                testDispatcher.advanceUntilIdle()

                var topLayer = layerManager.highestLayer.first()
                assert(topLayer != null)
                assert(topLayer == layer)

                val currentStack = fragmentsController.currentStack
                assert(currentStack.map { it.layer } == stack.map { it })
                assert(currentStack.last().content is LayerContents.Initialization)
                assert(currentStack.last().content.id == dummy.content.id)
            }
        }
    }

    @Test
    @Ignore("CENTAUR-529")
    fun `when show new layer counter order then top keeps the same`() {
        runBlockingTest {
            var knownId: UUID? = null
            var stack = ArrayList<Layer>()
            for (layer in Layer.list(true)) {
                stack.add(0, layer)

                layerManager.show(layer, makeDummyLayerInfo())
                testDispatcher.advanceUntilIdle()

                var topLayer = layerManager.highestLayer.first()
                assert(topLayer != null)
                assert(topLayer == Layer.ALARM)

                val currentStack = fragmentsController.currentStack
                assert(currentStack.map { it.layer } == stack.map { it })
                assert(currentStack.last().content is LayerContents.Initialization)
                if (knownId == null) {
                    knownId == currentStack.last().content.id
                } else {
                    assert(knownId == currentStack.last().content.id)
                }
            }
        }
    }

    @Test
    fun `when hide layers from top then top updates`() {
        runBlockingTest {
            for (layer in Layer.list(false)) {
                layerManager.show(layer, makeDummyLayerInfo())
                testDispatcher.advanceUntilIdle()
            }

            val dropOrder = Layer.list(true)
            for (i in 0 until dropOrder.size - 1) { // skip last intentionally
                layerManager.hide(dropOrder[i], benchmarkTimer = null)
                testDispatcher.advanceUntilIdle()

                val topLayer = layerManager.highestLayer.first()
                assert(topLayer != null)
                assert(topLayer == dropOrder[i + 1])
            }
        }
    }

    @Test
    fun `when hide layer from bottom then top keeps the same`() {
        runBlockingTest {
            for (layer in Layer.list(false)) {
                layerManager.show(layer, makeDummyLayerInfo())
                testDispatcher.advanceUntilIdle()
            }

            val dropOrder = Layer.list(false).drop(1)
            for (i in dropOrder.indices) {
                layerManager.hide(dropOrder[i], benchmarkTimer = null)
                testDispatcher.advanceUntilIdle()

                val topLayer = layerManager.highestLayer.first()
                assert(topLayer != null)
                if (i == dropOrder.size - 1) {
                    assert(topLayer == Layer.ROOT)
                } else {
                    assert(topLayer == Layer.ALARM)
                }
            }
        }
    }

    @Test
    fun `when clear layers requested then it removes everything`() {
        runBlockingTest {
            for (layer in Layer.list(false)) {
                layerManager.show(layer, makeDummyLayerInfo())
                testDispatcher.advanceUntilIdle()
            }

            layerManager.clear()
            testDispatcher.advanceUntilIdle()

            assert(layerManager.highestLayer.first() == null)
        }
    }

    @Test
    fun `when go to root requested then go to root layer`() {
        runBlockingTest {
            for (layer in Layer.list(false)) {
                layerManager.show(layer, makeDummyLayerInfo())
                testDispatcher.advanceUntilIdle()
            }

            // NOTE: thrice to check idempotency
            for (i in 0..2) {
                layerManager.goToRoot()
                testDispatcher.advanceUntilIdle()

                val topLayer = layerManager.highestLayer.first()
                assert(topLayer != null)
                assert(topLayer == Layer.ROOT)
            }
        }
    }

    private fun makeDummyLayerInfo(): LayerInfo {
        return LayerInfo(
            LayerContents.Initialization { SplashFragment() },
            LayerInfo.LifecycleConfiguration()
        )
    }

    private class FakeLayerItemComposition(
        override val content: LayerContents,
        override val layer: Layer,
        override var restorationData: RestorationData?,
        override val id: UUID,
        override val isExpired: Flow<Boolean>
    ) : LayerItemComposition {
        override fun launch(block: suspend () -> Unit) {}
        override suspend fun join() {}
        override fun onDestroy(benchmarkTimer: BenchmarkTimer?) {}
        override fun onFragmentRemoved() {}
    }
}
