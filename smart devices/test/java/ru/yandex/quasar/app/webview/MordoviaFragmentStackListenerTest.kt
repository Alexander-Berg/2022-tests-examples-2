package ru.yandex.quasar.app.webview

import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.BaseTest
import ru.yandex.quasar.app.FirstStartFragment
import ru.yandex.quasar.app.fragment_stack.FragmentFactory
import ru.yandex.quasar.app.fragment_stack.StackItem
import ru.yandex.quasar.app.webview.cache.SnapshotCache
import ru.yandex.quasar.app.webview.mordovia.MordoviaLoginErrorListener
import ru.yandex.quasar.app.webview.yabro.YabroViewProvider
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.fakes.FakeWebViewWrapper
import ru.yandex.quasar.fakes.FakeYabroViewProvider
import ru.yandex.quasar.shadows.ShadowLogger

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowLogger::class], instrumentedPackages = ["ru.yandex.quasar.util"])
class MordoviaFragmentStackListenerTest : BaseTest() {

    private lateinit var yabroViewProvider: YabroViewProvider
    private lateinit var snapshotCache: SnapshotCache
    private lateinit var metricaReporter: FakeMetricaReporter
    private lateinit var fragmentStackListener: MordoviaFragmentStackListener

    @Before
    fun setUp() {
        yabroViewProvider = FakeYabroViewProvider()
        metricaReporter = FakeMetricaReporter()
        snapshotCache = mock()
        fragmentStackListener =
            MordoviaFragmentStackListener(yabroViewProvider, snapshotCache, metricaReporter)
    }

    @Test
    fun when_TransitionFromOtherToMordovia_then_shouldStartNewNavigationSession() {
        val fromStack = StackItem.Builder(NON_YABROVIEW_FRAGMENT_FACTORY).build()
        val toStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()

        val webView = yabroViewProvider.get(0, MordoviaLoginErrorListener { }) as FakeWebViewWrapper
        fragmentStackListener.onBeforeStackChange(fromStack, toStack, true, false) // forward
        fragmentStackListener.onAfterStackChange(toStack)

        Assert.assertEquals(webView.newNavigationSessionStartedCount, 1)

        fragmentStackListener.onBeforeStackChange(fromStack, toStack, false, false) // backward
        fragmentStackListener.onAfterStackChange(toStack)

        Assert.assertEquals(webView.newNavigationSessionStartedCount, 2)
    }

    @Test
    fun when_TransitionFromMordoviaToOther_then_shouldSaveStateAndGoToBlank() {
        val fromStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()
        val toStack = StackItem.Builder(NON_YABROVIEW_FRAGMENT_FACTORY).build()

        val webView = yabroViewProvider.get(0, MordoviaLoginErrorListener { }) as FakeWebViewWrapper
        fragmentStackListener.onBeforeStackChange(fromStack, toStack, true, true) // forward
        fragmentStackListener.onAfterStackChange(toStack)

        Assert.assertEquals(webView.navigationSessionSavesCount, 1)
        Assert.assertEquals(webView.loadUrlCalled.size, 1)
        Assert.assertEquals(webView.loadUrlCalled[0].url, "about:blank")
        Assert.assertNull(webView.loadUrlCalled[0].scenario)

        fragmentStackListener.onBeforeStackChange(fromStack, toStack, false, false) // backward
        fragmentStackListener.onAfterStackChange(toStack)

        Assert.assertEquals(webView.navigationSessionSavesCount, 1) // should not change
        Assert.assertEquals(webView.loadUrlCalled.size, 2)
        Assert.assertEquals(webView.loadUrlCalled[1].url, "about:blank")
        Assert.assertNull(webView.loadUrlCalled[1].scenario)
    }

    @Test
    fun when_TransitionFromMordoviaToMordovia_then_shouldSaveStateAndStartNewNavSession() {
        val fromStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()
        val toStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()

        val webView = yabroViewProvider.get(0, MordoviaLoginErrorListener { }) as FakeWebViewWrapper
        fragmentStackListener.onBeforeStackChange(fromStack, toStack, true, true) // forward with saving state
        fragmentStackListener.onAfterStackChange(toStack)

        Assert.assertEquals(webView.navigationSessionSavesCount, 1)
        Assert.assertEquals(webView.newNavigationSessionStartedCount, 1)

        fragmentStackListener.onBeforeStackChange(fromStack, toStack, true, false) // forward without saving state
        fragmentStackListener.onAfterStackChange(toStack)

        Assert.assertEquals(webView.navigationSessionSavesCount, 1) // should not change
        Assert.assertEquals(webView.newNavigationSessionStartedCount, 2)

        fragmentStackListener.onBeforeStackChange(fromStack, toStack, false, false) // backward
        fragmentStackListener.onAfterStackChange(toStack)

        Assert.assertEquals(webView.navigationSessionSavesCount, 1) // should not change
        Assert.assertEquals(webView.newNavigationSessionStartedCount, 3)
    }

    @Test
    fun when_TransitionFromMordoviaAndSaveCurrentState_then_shouldMakeSnapshot() {
        whenever(snapshotCache.isAnyCacheAvailable).thenReturn(true)

        val fromStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()
        val toStack = StackItem.Builder(NON_YABROVIEW_FRAGMENT_FACTORY).build()

        val webView = yabroViewProvider.get(0, MordoviaLoginErrorListener { }) as FakeWebViewWrapper
        webView.loadUrl("testUrl", "testScenario", null)
        fragmentStackListener.onBeforeStackChange(fromStack, toStack, true, true) // forward with saving state
        fragmentStackListener.onAfterStackChange(toStack)

        verify(snapshotCache).save(eq("testScenario"), any())
        Assert.assertEquals(WebViewEvents.WEB_VIEW_SNAPSHOT, metricaReporter.latencyPoints.last())
        val lastLatency = metricaReporter.latencies.last()
        Assert.assertEquals(WebViewEvents.WEB_VIEW_SNAPSHOT, lastLatency.pointName)
        Assert.assertEquals(WebViewEvents.WEB_VIEW_SNAPSHOT_ACQUIRED, lastLatency.eventName)
        Assert.assertTrue(lastLatency.removePoint)
    }

    @Test
    fun when_TransitionForward_then_shouldBlockCacheAcquiring() {
        val fromStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()
        val toStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()

        yabroViewProvider.get(0, MordoviaLoginErrorListener { })
        fragmentStackListener.onBeforeStackChange(fromStack, toStack, true, false) // forward with saving state
        fragmentStackListener.onAfterStackChange(toStack)

        verify(snapshotCache).cacheAcquiringBlocked = true
    }

    @Test
    fun when_TransitionBackward_then_shouldNotBlockCacheAcquiring() {
        val fromStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()
        val toStack = StackItem.Builder(YABROVIEW_FRAGMENT_FACTORY).build()

        yabroViewProvider.get(0, MordoviaLoginErrorListener { })
        fragmentStackListener.onBeforeStackChange(fromStack, toStack, false, false) // forward with saving state
        fragmentStackListener.onAfterStackChange(toStack)

        verify(snapshotCache).cacheAcquiringBlocked = false
    }

    private class YabroViewFragmentFactory : FragmentFactory<YabroViewFragment> {
        override fun newInstance(): YabroViewFragment {
            throw RuntimeException()
        }

        override fun getFragmentClass(): Class<YabroViewFragment> {
            return YabroViewFragment::class.java
        }
    }

    private class NonYabroViewFragmentFactory : FragmentFactory<FirstStartFragment> {
        override fun newInstance(): FirstStartFragment {
            throw RuntimeException()
        }

        override fun getFragmentClass(): Class<FirstStartFragment> {
            return FirstStartFragment::class.java
        }
    }

    companion object {
        private val YABROVIEW_FRAGMENT_FACTORY = YabroViewFragmentFactory()
        private val NON_YABROVIEW_FRAGMENT_FACTORY = NonYabroViewFragmentFactory()
    }
}
