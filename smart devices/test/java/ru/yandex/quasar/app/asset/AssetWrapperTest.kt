package ru.yandex.quasar.app.asset

import androidx.core.util.Consumer
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers.any
import org.mockito.ArgumentMatchers.anyBoolean
import org.mockito.Mockito.`when`
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.robolectric.RobolectricTestRunner
import java.io.IOException
import java.util.concurrent.ExecutorService

@RunWith(RobolectricTestRunner::class)
class AssetWrapperTest {

    @Test
    fun loadAssetStartsReading() {
        val assetReader = mock(AssetReader::class.java)
        val workerService = mock(ExecutorService::class.java)
        `when`(workerService.execute(any())).then { (it.arguments[0] as Runnable).run() }
        val assetWrapper = AssetWrapper(assetReader, workerService, "TestAsset")
        assetWrapper.loadAsset()
        verify(assetReader).readAsset(any(), anyBoolean())
    }

    @Test
    fun assetConsumersAreConsumedAfterReading() {
        val assetConsumer1 = mock(Consumer::class.java) as Consumer<String>
        val assetConsumer2 = mock(Consumer::class.java) as Consumer<String>
        val assetConsumer3 = mock(Consumer::class.java) as Consumer<String>

        val assetReader = mock(AssetReader::class.java)
        val workerService = mock(ExecutorService::class.java)
        val pendingTask = arrayOfNulls<Runnable>(1)
        `when`(workerService.execute(any())).then {
            pendingTask.set(0, it.arguments[0] as Runnable)
        }
        val assetWrapper = AssetWrapper(assetReader, workerService, "TestAsset")
        assetWrapper.doWithAsset(assetConsumer1)
        assetWrapper.doWithAsset(assetConsumer2)
        assetWrapper.doWithAsset(assetConsumer3)
        pendingTask[0]!!.run()
        verify(assetConsumer1).accept(any())
        verify(assetConsumer2).accept(any())
        verify(assetConsumer3).accept(any())
    }

    @Test(expected = RuntimeException::class)
    fun doOnFailIsCalledOnFail() {
        val assetReader = mock(AssetReader::class.java)
        `when`(assetReader.readAsset(any(), anyBoolean())).then { throw IOException("No file") }
        val workerService = mock(ExecutorService::class.java)
        `when`(workerService.execute(any())).then { (it.arguments[0] as Runnable).run() }
        val assetWrapper = AssetWrapper(assetReader, workerService, "TestAsset")
        assetWrapper.loadAsset()
    }

    @Test
    fun assetConsumerIsCalledIfAssetIsRead() {
        val assetConsumer = mock(Consumer::class.java) as Consumer<String>
        val assetReader = mock(AssetReader::class.java)
        `when`(assetReader.readAsset(any(), anyBoolean())).thenReturn("alert(\"Hello World!\");")
        val workerService = mock(ExecutorService::class.java)
        `when`(workerService.execute(any())).then { (it.arguments[0] as Runnable).run() }
        val assetWrapper = AssetWrapper(assetReader, workerService, "TestAsset")
        assetWrapper.loadAsset()
        assetWrapper.doWithAsset(assetConsumer)
        verify(assetReader).readAsset(any(), anyBoolean())
        verify(assetConsumer).accept(any())
    }
}