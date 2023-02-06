package ru.yandex.quasar.app.fragment_stack

import ru.yandex.quasar.app.webview.MordoviaConfiguration
import ru.yandex.quasar.app.webview.MordoviaConfigurationFactory
import ru.yandex.quasar.app.webview.YabroViewFragment
import ru.yandex.quasar.app.webview.mordovia.configuration.MordoviaConfigurationKeeper

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.BaseTest
import ru.yandex.quasar.app.main.MainFragment
import ru.yandex.quasar.app.services.GroupObservable
import ru.yandex.quasar.fakes.FakeConfiguration
import ru.yandex.quasar.fakes.FakeQuasarConnector
import ru.yandex.quasar.shadows.ShadowLogger

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowLogger::class], instrumentedPackages = ["ru.yandex.quasar.util"])
class HomeFragmentFactoryProviderTest : BaseTest() {

    @Test
    fun given_EmptyCachedFactory_when_requestToBuildMordoviaFactory_then_DoIt() {
        val configuration = makeMordoviaConfiguration()
        val keeper = FakeMordoviaConfigurationKeeper(configuration)
        val factoryProvider = HomeFragmentFactoryProvider(keeper, makeGroupObservable())
        val factory = factoryProvider.invoke(null)
        Assert.assertTrue(factory.fragmentClass == YabroViewFragment::class.java)
    }

    @Test
    fun given_EmptyCachedFactory_when_requestToBuildNativeFactory_then_DoIt() {
        val keeper = FakeMordoviaConfigurationKeeper(null)
        val factoryProvider = HomeFragmentFactoryProvider(keeper, makeGroupObservable())
        val factory = factoryProvider.invoke(null)
        Assert.assertTrue(factory.fragmentClass == MainFragment::class.java)
    }

    @Test
    fun given_CachedMordoviaFactory_when_requestToBuildSameMordoviaFactory_then_ReturnCached() {
        val configuration = makeMordoviaConfiguration()
        val keeper = FakeMordoviaConfigurationKeeper(configuration)
        val factoryProvider = HomeFragmentFactoryProvider(keeper, makeGroupObservable())
        val factory1 = factoryProvider.invoke(null)
        Assert.assertTrue(factory1.fragmentClass == YabroViewFragment::class.java)

        val factory2 = factoryProvider.invoke(null)
        Assert.assertEquals(factory1, factory2)
        Assert.assertTrue(factory2.fragmentClass == YabroViewFragment::class.java)
    }

    @Test
    fun given_CachedMordoviaFactory_when_requestToBuildAnotherMordoviaFactory_then_BuildNew() {
        val configuration1 = makeMordoviaConfiguration()
        val keeper = FakeMordoviaConfigurationKeeper(configuration1)
        val factoryProvider = HomeFragmentFactoryProvider(keeper, makeGroupObservable())
        val factory1 = factoryProvider.invoke(null)
        Assert.assertTrue(factory1.fragmentClass == YabroViewFragment::class.java)

        val configuration2 = makeMordoviaConfiguration("http://yandex.ru")
        keeper.configuration = configuration2
        val factory2 = factoryProvider.invoke(null)
        Assert.assertNotEquals(factory1, factory2)
        Assert.assertTrue(factory2.fragmentClass == YabroViewFragment::class.java)
    }

    @Test
    fun given_CachedMordoviaFactory_when_requestToBuildNativeFactory_then_DoIt() {
        val configuration1 = makeMordoviaConfiguration()
        val keeper = FakeMordoviaConfigurationKeeper(configuration1)
        val factoryProvider = HomeFragmentFactoryProvider(keeper, makeGroupObservable())
        val factory1 = factoryProvider.invoke(null)
        Assert.assertTrue(factory1.fragmentClass == YabroViewFragment::class.java)

        keeper.configuration = null
        val factory2 = factoryProvider.invoke(null)
        Assert.assertNotEquals(factory1, factory2)
        Assert.assertTrue(factory2.fragmentClass == MainFragment::class.java)
    }

    @Test
    fun given_CachedNativeFactory_when_requestedToBuildMordoviaFactory_then_DoIt() {
        val keeper = FakeMordoviaConfigurationKeeper(null)
        val factoryProvider = HomeFragmentFactoryProvider(keeper, makeGroupObservable())
        val factory1 = factoryProvider.invoke(null)
        Assert.assertTrue(factory1.fragmentClass == MainFragment::class.java)

        val configuration1 = makeMordoviaConfiguration()
        keeper.configuration = configuration1
        val factory2 = factoryProvider.invoke(null)
        Assert.assertNotEquals(factory1, factory2)
        Assert.assertTrue(factory2.fragmentClass == YabroViewFragment::class.java)
    }

    private fun makeGroupObservable(): GroupObservable {
        val fakeConfiguration = FakeConfiguration()
        fakeConfiguration.initialize("{}")
        return GroupObservable(fakeConfiguration, FakeQuasarConnector())
    }

    private fun makeMordoviaConfiguration(
            url: String = "http://example.com"
    ): MordoviaConfiguration {
        val factory = MordoviaConfigurationFactory()
        return factory.makeConfigurationFromScratch(
                url,
                "test",
                null,
                null,
                null,
                null,
                StackItem.StackBehavior.DEFAULT
        )
    }

    private class FakeMordoviaConfigurationKeeper(
            var configuration: MordoviaConfiguration?,
            var requiredToStore: MutableList<MordoviaConfiguration> = ArrayList(),
            var requiredToDrop: Int = 0
    ): MordoviaConfigurationKeeper {
        override fun store(configuration: MordoviaConfiguration) {
            requiredToStore.add(configuration)
        }

        override fun drop() {
            requiredToDrop += 1
        }

        override fun acquire(): MordoviaConfiguration? {
            return configuration
        }

    }
}
