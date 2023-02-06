package ru.yandex.quasar.app.screensaver.screenSaverConfigurators

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import junit.framework.TestCase.*
import okhttp3.Request
import okhttp3.Response
import okhttp3.ResponseBody
import org.assertj.core.api.Assertions.assertThat
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.spy
import org.mockito.kotlin.any
import org.mockito.kotlin.doAnswer
import org.mockito.kotlin.eq
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.screensaver.screenSaverHelpers.ScreenSaverItemGsonConverter
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverImageItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItemsCollection
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverVideoItem
import ru.yandex.quasar.app.utils.HttpClient
import ru.yandex.quasar.fakes.FakeExecutorService
import ru.yandex.quasar.shadows.ShadowLogger

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowLogger::class], instrumentedPackages = ["ru.yandex.quasar.util"])
class ScreenSaverBackendConfiguratorTest {

    private val httpClient: HttpClient = mock()
    private val builder: Request.Builder = mock()
    private val response: Response = mock()
    private val fakeExecutorService = FakeExecutorService()
    private val spyScreenSaverGson: Gson

    init {
        val simpleGson = GsonBuilder().serializeNulls().create()
        val screenSaverGson = GsonBuilder()
            .registerTypeHierarchyAdapter(
                ScreenSaverItem::class.java,
                ScreenSaverItemGsonConverter(simpleGson)
            )
            .serializeNulls()
            .create()
        spyScreenSaverGson = spy(screenSaverGson)
    }

    private fun initResponse(code: Int, responseBody: String? = null) {
        whenever(httpClient.newRequest()).thenReturn(builder)
        whenever(builder.url(any<String>())).thenReturn(builder)
        val body: ResponseBody = mock()
        whenever(response.code).thenReturn(code)
        if (responseBody != null) {
            whenever(response.body).thenReturn(body)
            whenever(body.string()).thenReturn(responseBody)
        }
        whenever(httpClient.execute(any(), any())).doAnswer {
            val withResponse = it.getArgument(1) as HttpClient.ResponseConsumer
            withResponse.operate(response)
        }
    }

    @Test
    fun given_badHttpResponse_when_createBackendConfigurator_then_fewRequestAttempts() {
        // init response with 500 error
        initResponse(500)

        // create backend configurator
        ScreenSaverBackendConfigurator(
            "testUrl",
            spyScreenSaverGson,
            httpClient,
            fakeExecutorService
        )

        fakeExecutorService.runAllJobsRecursive()

        // httpClient.execute has to be called 4 times
        verify(httpClient, times(4)).execute(any(), any())
        // we don't get any response so collection wasn't deserialized
        verify(spyScreenSaverGson, never()).fromJson(
            any<String>(),
            eq(ScreenSaverItemsCollection::class.java)
        )
    }

    @Test
    fun given_invalidJson_when_createBackendConfigurator_then_oneAttempt() {
        // init response with 200 and invalid json
        initResponse(200, "not a json")

        // create backend configurator
        val backendConfigurator = ScreenSaverBackendConfigurator(
            "testUrl",
            spyScreenSaverGson,
            httpClient,
            fakeExecutorService
        )
        fakeExecutorService.runAllJobs()

        // httpClient.execute has to be called successfully 1 time and 1 try to parse config
        inOrder(httpClient, spyScreenSaverGson) {
            verify(httpClient).execute(any(), any())
            verify(spyScreenSaverGson).fromJson(
                any<String>(),
                eq(ScreenSaverItemsCollection::class.java)
            )
        }
        // no items in collection
        assertNull(backendConfigurator.next)
    }

    @Test
    fun given_goodHttpResponse_when_createBackendConfigurator_then_initOk() {
        // init response with 200 and one item
        val item = ScreenSaverImageItem("testUrl")
        val jsonResponse = spyScreenSaverGson.toJson(ScreenSaverItemsCollection(listOf(item)))
        initResponse(200, jsonResponse)

        // create backend configurator
        val backendConfigurator = ScreenSaverBackendConfigurator(
            "testUrl",
            spyScreenSaverGson,
            httpClient,
            fakeExecutorService
        )
        fakeExecutorService.runAllJobs()

        // httpClient.execute will be called 1 time and we will parse collection after it
        inOrder(httpClient, spyScreenSaverGson) {
            verify(httpClient).execute(any(), any())
            verify(spyScreenSaverGson).fromJson(
                any<String>(),
                eq(ScreenSaverItemsCollection::class.java)
            )
        }
        assertThat(backendConfigurator.next).isEqualToComparingFieldByField(item)
    }

    @Test
    fun given_backendConfiguratorWithEmptyCollection_when_getNextItem_then_loadNewConfig() {
        // create backend configurator with empty collection
        val collection = ScreenSaverItemsCollection(listOf())
        val jsonResponse = spyScreenSaverGson.toJson(collection)
        initResponse(200, jsonResponse)
        val backendConfigurator =
            spy(
                ScreenSaverBackendConfigurator(
                    "testUrl",
                    spyScreenSaverGson,
                    httpClient,
                    fakeExecutorService
                )
            )
        fakeExecutorService.runAllJobs()

        // test new loading has been started
        inOrder(httpClient, spyScreenSaverGson, backendConfigurator) {
            // verify backend load items
            verify(httpClient).execute(any(), any())
            verify(spyScreenSaverGson).fromJson(
                any<String>(),
                eq(ScreenSaverItemsCollection::class.java)
            )

            // get next item
            assertNull(backendConfigurator.next)
            fakeExecutorService.runAllJobs()

            // verify new loading has been started
            verify(httpClient).execute(any(), any())
            verify(spyScreenSaverGson).fromJson(
                any<String>(),
                eq(ScreenSaverItemsCollection::class.java)
            )
        }
    }

    @Test
    fun given_backendConfiguratorWithItems_when_getNextItem_then_nextItemIsCorrect() {
        //  init response with 2 items
        val imageItem = ScreenSaverImageItem("imageUrl")
        val videoItem = ScreenSaverVideoItem("videoUrl")
        val itemsCollection = ScreenSaverItemsCollection(listOf(imageItem, videoItem))
        val jsonResponse = spyScreenSaverGson.toJson(itemsCollection)
        initResponse(200, jsonResponse)

        // create backend configurator
        val backendConfigurator =
            ScreenSaverBackendConfigurator(
                "testUrl",
                spyScreenSaverGson,
                httpClient,
                fakeExecutorService
            )
        fakeExecutorService.runAllJobs()

        // check configurator has been initialized
        inOrder(httpClient, spyScreenSaverGson) {
            verify(httpClient).execute(any(), any())
            verify(spyScreenSaverGson).fromJson(
                any<String>(),
                eq(ScreenSaverItemsCollection::class.java)
            )
        }

        // check next items are correct
        assertThat(backendConfigurator.next).isEqualToComparingFieldByField(imageItem)
        assertThat(backendConfigurator.next).isEqualToComparingFieldByField(videoItem)
        assertThat(backendConfigurator.next).isEqualToComparingFieldByField(imageItem)
    }

    @Test
    fun given_httpBadResponse_when_createAndDestroyConfigurator_then_loadingHasBeenStopped() {
        // init response with 500 error
        initResponse(500)

        // create backend configurator
        val backendConfigurator = ScreenSaverBackendConfigurator(
            "testUrl",
            spyScreenSaverGson,
            httpClient,
            fakeExecutorService
        )

        assertEquals(1, fakeExecutorService.items.size)
        val executingItem = fakeExecutorService.items.values.first()
        val future = executingItem.future!!

        // destroy backend configurator
        backendConfigurator.destroy()

        // task has to be cancelled
        assertTrue(future.isCancelled)
    }
}
