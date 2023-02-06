package ru.yandex.quasar.app.screensaver.screenSaverHelpers

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.google.gson.reflect.TypeToken
import okhttp3.Request
import okhttp3.Response
import okhttp3.ResponseBody
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.spy
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.doAnswer
import org.mockito.kotlin.eq
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.powermock.api.mockito.PowerMockito
import org.powermock.core.classloader.annotations.PrepareForTest
import org.powermock.modules.junit4.PowerMockRunner
import ru.yandex.quasar.app.screensaver.screenSaverHelpers.writers.ScreenSaverWriter
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverImageItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverVideoItem
import ru.yandex.quasar.app.screensaver.screenSaverMediaItems.ScreenSaverDiskItem
import ru.yandex.quasar.app.utils.HttpClient
import ru.yandex.quasar.fakes.FakeExecutorService
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.ScheduledFuture

@RunWith(PowerMockRunner::class)
@PrepareForTest(ScreenSaverMediaLoader::class)
class ScreenSaverMediaLoaderTest {

    private val screenSaverWriter: ScreenSaverWriter = mock()
    private val fakeExecutorService = FakeExecutorService()
    private val httpClient: HttpClient = mock()
    private val builder: Request.Builder = mock()
    private val response: Response = mock()
    private val context: Context = mock()
    private val sharedPrefs: SharedPreferences = mock()
    private val spyScreenSaverGson: Gson
    private val mediaLoadListener: ScreenSaverMediaLoader.MediaLoadListener = mock()
    private val url: URL = mock()
    private val urlConnection: HttpURLConnection = mock()

    private val scheduledExecutorService: ScheduledExecutorService = mock()
    private val future: ScheduledFuture<Any> = mock()

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

    @Before
    fun setUp() {
        whenever(
            context.getSharedPreferences(
                any(),
                eq(Context.MODE_PRIVATE)
            )
        ).thenReturn(sharedPrefs)
        whenever(sharedPrefs.edit()).thenReturn(mock())
        whenever(httpClient.newRequest()).thenReturn(builder)
        whenever(builder.url(any<String>())).thenReturn(builder)

        whenever(httpClient.execute(any(), any())).doAnswer {
            val withResponse = it.getArgument(1) as HttpClient.ResponseConsumer
            withResponse.operate(response)
        }

        PowerMockito.whenNew(URL::class.java).withAnyArguments().thenReturn(url)
        whenever(url.openConnection()).thenReturn(urlConnection)
        whenever(urlConnection.getHeaderField(eq("content-length"))).thenReturn("0")

        whenever(future.isDone).thenReturn(true)
        whenever(future.cancel(any())).thenReturn(true)

        argumentCaptor<Runnable>().apply {
            whenever(scheduledExecutorService.submit(capture())).doAnswer {
                val executedTask = firstValue
                executedTask.run()
                future
            }
        }

        argumentCaptor<Runnable>().apply {
            whenever(scheduledExecutorService.schedule(capture(), any(), any())).doAnswer {
                val executedTask = firstValue
                executedTask.run()
                future
            }
        }
    }

    @Test
    fun given_noPreferences_when_createMediaLoader_then_noInitialization() {
        ScreenSaverMediaLoader(
            context,
            screenSaverWriter,
            fakeExecutorService,
            httpClient,
            spyScreenSaverGson
        )

        verify(spyScreenSaverGson, never())
            .fromJson<List<ScreenSaverItem>>(
                any<String>(),
                eq(object : TypeToken<List<ScreenSaverItem>>() {}.type)
            )
    }

    @Test
    fun given_preferences_when_createMediaLoader_then_noInitialization() {
        // init prefs with empty list
        val jsonPrefs = spyScreenSaverGson.toJson(listOf<ScreenSaverItem>())
        whenever(sharedPrefs.getString(any(), eq(null))).thenReturn(jsonPrefs)

        // create media loader
        ScreenSaverMediaLoader(
            context,
            screenSaverWriter,
            fakeExecutorService,
            httpClient,
            spyScreenSaverGson
        )

        // init loader with config
        verify(spyScreenSaverGson)
            .fromJson<List<ScreenSaverItem>>(
                any<String>(),
                eq(object : TypeToken<List<ScreenSaverItem>>() {}.type)
            )
    }

    @Test
    fun given_mediaLoaderWithEmptyItems_when_addItem_then_itemStartLoading() {
        // create media loader without items
        whenever(screenSaverWriter.isItemLoaded(any())).thenReturn(false)
        val mediaLoader = ScreenSaverMediaLoader(
            context,
            screenSaverWriter,
            fakeExecutorService,
            httpClient,
            spyScreenSaverGson
        )

        // add item to media loader
        val imageItem = ScreenSaverImageItem("imageUrl")
        mediaLoader.addItem(imageItem)

        // old items not removed and item is start loading
        verify(screenSaverWriter, never()).removeOldItems(eq(null))
        verify(screenSaverWriter).isItemLoaded(eq(imageItem))
        assertEquals(1, fakeExecutorService.items.size)
    }

    @Test
    fun given_mediaLoaderWithItems_when_addItem_then_oldItemsDeletedAndNewItemStartLoading() {
        // create media loader without items
        val imageItem = ScreenSaverImageItem("imageUrl")
        val videoItem = ScreenSaverVideoItem("videoUrl")
        val jsonPrefs = spyScreenSaverGson.toJson(listOf(imageItem, videoItem))
        whenever(sharedPrefs.getString(any(), eq(null))).thenReturn(jsonPrefs)
        val mediaLoader = ScreenSaverMediaLoader(
            context,
            screenSaverWriter,
            fakeExecutorService,
            httpClient,
            spyScreenSaverGson
        )

        // add new item to media loader
        val imageItem2 = ScreenSaverImageItem("imageUrl2")
        mediaLoader.addItem(imageItem2)

        // old items removed and new item is start loading
        inOrder(screenSaverWriter) {
            verify(screenSaverWriter).removeOldItems(eq(null))
            verify(screenSaverWriter).isItemLoaded(eq(imageItem2))
        }
        assertEquals(1, fakeExecutorService.items.size)
    }

    @Test
    fun given_mediaLoader_when_clearQueue_then_writerQueueCleared() {
        // create media loader
        val mediaLoader = ScreenSaverMediaLoader(
            context,
            screenSaverWriter,
            fakeExecutorService,
            httpClient,
            spyScreenSaverGson
        )

        // clear queue
        mediaLoader.clearQueue()

        // loaded items removed and state saved
        inOrder(screenSaverWriter, sharedPrefs) {
            verify(screenSaverWriter).removeLoadedItems(eq(null))
            verify(sharedPrefs).edit()
            verify(screenSaverWriter).saveState()
        }
    }

    @Test
    fun given_mediaLoader_when_removeItem_then_itemRemovedFromWriter() {
        // create media loader
        val mediaLoader = ScreenSaverMediaLoader(
            context,
            screenSaverWriter,
            fakeExecutorService,
            httpClient,
            spyScreenSaverGson
        )

        // remove item from media loader
        val imageItem = ScreenSaverImageItem("imageUrl")
        mediaLoader.removeItem(imageItem)

        // item removed from writer
        verify(screenSaverWriter).remove(eq(imageItem))
    }

    @Test
    fun given_mediaLoader_when_addItem_then_itemIsLoaded() {
        // init response for loading item
        whenever(screenSaverWriter.canLoadNewMediaItem(any())).thenReturn(true)
        whenever(response.code).thenReturn(200)
        val body: ResponseBody = mock()
        whenever(response.body).thenReturn(body)
        whenever(body.byteStream()).thenReturn(mock())
        // mock saving
        val mediaItem: ScreenSaverDiskItem = mock()
        whenever(screenSaverWriter.save(any())).thenReturn(mediaItem)

        // create mediaLoader
        val mediaLoader = ScreenSaverMediaLoader(
            context,
            screenSaverWriter,
            fakeExecutorService,
            httpClient,
            spyScreenSaverGson
        )
        mediaLoader.addListener(mediaLoadListener)

        // add item to media loader
        val imageItem = ScreenSaverImageItem("imageUrl")
        mediaLoader.addItem(imageItem)
        fakeExecutorService.runAllJobsRecursive()

        // item has to be loaded
        verify(mediaLoadListener).onMediaLoaded(
            mediaItem,
            ScreenSaverMediaLoader.ScreenSaverItemSource.NETWORK
        )
    }

    @Test
    fun given_mediaLoader_when_destroy_then_loadingStopped() {
        // init bad response and create media loader
        whenever(screenSaverWriter.canLoadNewMediaItem(any())).thenReturn(true)
        whenever(response.code).thenReturn(500)
        val mediaLoader = ScreenSaverMediaLoader(
            context,
            screenSaverWriter,
            fakeExecutorService,
            httpClient,
            spyScreenSaverGson
        )

        // add item to media loader
        mediaLoader.addItem(ScreenSaverImageItem("imageUrl"))
        // run adding item
        fakeExecutorService.runAllJobs()

        // save and run httpClient request
        assertEquals(1, fakeExecutorService.items.size)
        val executingItem = fakeExecutorService.items.values.first()
        val future = executingItem.future!!
        fakeExecutorService.runAllJobs()

        // loading had been started
        verify(httpClient).execute(any(), any())

        // destroy media loader, loading has been stopped and old items has been deleted
        mediaLoader.destroy()
        verify(screenSaverWriter).removeOldItems(eq(null))
        assertTrue(future.isCancelled)
    }
}
