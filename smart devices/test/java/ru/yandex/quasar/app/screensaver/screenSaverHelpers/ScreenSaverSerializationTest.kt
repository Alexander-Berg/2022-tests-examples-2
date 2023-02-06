package ru.yandex.quasar.app.screensaver.screenSaverHelpers

import com.google.common.reflect.TypeToken
import com.google.gson.*
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.Assert.*
import org.junit.Test
import org.mockito.Mockito.mock
import org.mockito.kotlin.whenever
import ru.yandex.quasar.app.configs.ScreenSaverType
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverImageItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItem
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItemsCollection
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverVideoItem
import ru.yandex.quasar.app.screensaver.screenSaverMediaItems.ScreenSaverDiskItem
import ru.yandex.quasar.app.screensaver.screenSaverMediaItems.ScreenSaverMediaItem
import java.io.File

class ScreenSaverSerializationTest {
    private val screenSaverGson: Gson

    init {
        val simpleGson = GsonBuilder().serializeNulls().create()
        screenSaverGson = GsonBuilder()
            .registerTypeHierarchyAdapter(
                ScreenSaverItem::class.java,
                ScreenSaverItemGsonConverter(simpleGson)
            )
            .serializeNulls()
            .create()
    }

    @Test
    fun given_backendResponse_when_deserialize_then_itIsImageAndAllFieldsAreCorrect() {
        // backend response as string
        val screenSaverConfig =
            "{'files':[{'description':'Ключевская сопка. Антон Шкаплеров','url':'http://quasar.s3.yandex.net/backend/screensaver/31.jpg'}],'status':'ok'}"

        // deserialize response
        val collection =
            screenSaverGson.fromJson(screenSaverConfig, ScreenSaverItemsCollection::class.java)

        // check it is IMAGE and all fields are correct
        val item = collection.next as ScreenSaverImageItem
        assertNotNull(item)
        assertTrue(item.isValid)
        assertEquals("http://quasar.s3.yandex.net/backend/screensaver/31.jpg", item.url)
        assertEquals("Ключевская сопка. Антон Шкаплеров", item.description)
        assertEquals(ScreenSaverImageItem.DEFAULT_LOGO_URL, item.logo)
        assertEquals(ScreenSaverImageItem.DEFAULT_DURATION_MS, item.durationInMs)
    }

    @Test
    fun given_deserializedBackendResponse_when_serializeAndDeserialize_then_itemsAreEqual() {
        // deserialized backend response
        val screenSaverConfig =
            "{'files':[{'description':'Ключевская сопка. Антон Шкаплеров','url':'http://quasar.s3.yandex.net/backend/screensaver/31.jpg'}],'status':'ok'}"
        val collection =
            screenSaverGson.fromJson(screenSaverConfig, ScreenSaverItemsCollection::class.java)
        val item = collection.next as ScreenSaverImageItem

        // serialize and then deserialize it again
        val serializedCollection = screenSaverGson.toJson(collection)
        val deserializedCollection =
            screenSaverGson.fromJson(serializedCollection, ScreenSaverItemsCollection::class.java)

        // compare deserialized item and original
        val deserializedItem = deserializedCollection.next as ScreenSaverImageItem
        assertThat(deserializedItem).isEqualToComparingFieldByField(item)
    }

    @Test
    fun given_serializedImageItem_when_deserialize_then_itIsImageAndAllFieldsAreTheSame() {
        // format json item
        val jsonObject = JsonObject()
        jsonObject.addProperty("type", ScreenSaverType.IMAGE.name)
        jsonObject.addProperty("description", "Image")
        jsonObject.addProperty("url", "imageUrl")
        jsonObject.addProperty("logo", "logoUrl")
        jsonObject.addProperty("duration", 10000)
        val jsonImageItem = jsonObject.toString()

        // deserialize item
        val imageItem = screenSaverGson.fromJson(
            jsonImageItem,
            ScreenSaverItem::class.java
        ) as ScreenSaverImageItem

        // compare deserialized item and original
        assertTrue(imageItem.isValid)
        assertEquals(jsonObject["url"].asString, imageItem.url)
        assertEquals(jsonObject["description"].asString, imageItem.description)
        assertEquals(jsonObject["logo"].asString, imageItem.logo)
        assertEquals(jsonObject["duration"].asInt, imageItem.durationInMs)
    }

    @Test
    fun given_serializedVideoItem_when_deserialize_then_itIsVideoAndAllFieldsAreTheSame() {
        // format json item
        val jsonObject = JsonObject()
        jsonObject.addProperty("type", ScreenSaverType.VIDEO.name)
        jsonObject.addProperty("description", "Video")
        jsonObject.addProperty("url", "videoUrl")
        jsonObject.addProperty("logo", "logoUrl")
        jsonObject.addProperty("duration", 60000)
        val jsonVideoItem = jsonObject.toString()

        // deserialize item
        val videoItem = screenSaverGson.fromJson(
            jsonVideoItem,
            ScreenSaverItem::class.java
        ) as ScreenSaverVideoItem

        // compare deserialized item and original
        assertTrue(videoItem.isValid)
        assertEquals(jsonObject["url"].asString, videoItem.url)
        assertEquals(jsonObject["description"].asString, videoItem.description)
        assertEquals(jsonObject["logo"].asString, videoItem.logo)
        assertEquals(jsonObject["duration"].asInt, videoItem.durationInMs)
    }

    @Test
    fun given_serializedItemWithoutType_when_deserialize_then_itIsAnImage() {
        // format json item
        val jsonObject = JsonObject()
        jsonObject.addProperty("url", "defaultUrl")
        jsonObject.addProperty("description", "Default")
        val jsonDefaultItem = jsonObject.toString()

        // deserialize item
        val imageItem = screenSaverGson.fromJson(
            jsonDefaultItem,
            ScreenSaverItem::class.java
        ) as ScreenSaverImageItem

        // check all fields are correct
        assertTrue(imageItem.isValid)
        assertEquals(jsonObject["url"].asString, imageItem.url)
        assertEquals(jsonObject["description"].asString, imageItem.description)
        assertEquals(ScreenSaverImageItem.DEFAULT_LOGO_URL, imageItem.logo)
        assertEquals(ScreenSaverImageItem.DEFAULT_DURATION_MS, imageItem.durationInMs)
    }

    @Test
    fun given_serializedItemWithUnknownType_when_deserialize_then_jsonParseException() {
        // format json item
        val jsonObject = JsonObject()
        jsonObject.addProperty("type", "UNKNOWN")
        val jsonUnknownItem = jsonObject.toString()

        // deserialize item and catch JsonParseException
        assertThatThrownBy {
            screenSaverGson.fromJson(jsonUnknownItem, ScreenSaverItem::class.java)
        }.isInstanceOf(JsonParseException::class.java)
            .hasMessage("Unknown ScreenSaverItem type: UNKNOWN")
    }

    @Test
    fun given_serializedImageItemWithEmptyFields_when_deserialize_then_checkDefaultValues() {
        // format json item
        val jsonObject = JsonObject()
        jsonObject.addProperty("type", "IMAGE")
        val jsonImageItem = jsonObject.toString()

        // deserialize item
        val imageItem = screenSaverGson.fromJson(
            jsonImageItem,
            ScreenSaverItem::class.java
        ) as ScreenSaverImageItem

        // check default properties
        val expectedImageItem = ScreenSaverImageItem(
            "",
            null,
            ScreenSaverImageItem.DEFAULT_LOGO_URL,
            ScreenSaverImageItem.DEFAULT_DURATION_MS
        )
        assertThat(imageItem).isEqualToComparingFieldByField(expectedImageItem)
    }

    @Test
    fun given_serializedVideoItemWithEmptyFields_when_deserialize_then_checkDefaultValues() {
        // format json item
        val jsonObject = JsonObject()
        jsonObject.addProperty("type", "VIDEO")
        val jsonVideoItem = jsonObject.toString()

        // deserialize item
        val videoItem = screenSaverGson.fromJson(
            jsonVideoItem,
            ScreenSaverItem::class.java
        ) as ScreenSaverVideoItem

        // check default properties
        val expectedVideoItem =
            ScreenSaverImageItem("", null, null, ScreenSaverVideoItem.DEFAULT_DURATION_MS)
        assertThat(videoItem).isEqualToComparingFieldByField(expectedVideoItem)
    }

    @Test
    fun given_serializedConfigWithNullFields_when_deserialize_then_fieldsAreNull() {
        // format json item
        val jsonImageObject = JsonObject()
        jsonImageObject.addProperty("type", "IMAGE")
        jsonImageObject.addProperty("url", null as String?)
        jsonImageObject.addProperty("logo", null as String?)
        jsonImageObject.addProperty("duration", null as Int?)

        val jsonVideoObject = JsonObject()
        jsonVideoObject.addProperty("type", "VIDEO")
        jsonVideoObject.addProperty("url", null as String?)
        jsonVideoObject.addProperty("logo", null as String?)
        jsonVideoObject.addProperty("duration", null as Int?)

        val jsonCollectionArray = JsonArray()
        jsonCollectionArray.add(jsonImageObject)
        jsonCollectionArray.add(jsonVideoObject)

        val jsonCollectionObject = JsonObject()
        jsonCollectionObject.add("files", jsonCollectionArray)

        val jsonCollection = jsonCollectionObject.toString()

        // deserialize
        val collection =
            screenSaverGson.fromJson(jsonCollection, ScreenSaverItemsCollection::class.java)

        // check fields are null
        val imageItem = collection.next as ScreenSaverImageItem
        assertFalse(imageItem.isValid)
        assertNull(imageItem.url)
        assertNull(imageItem.description)
        assertNull(imageItem.logo)
        assertEquals(ScreenSaverImageItem.DEFAULT_DURATION_MS, imageItem.durationInMs)

        val videoItem = collection.next as ScreenSaverVideoItem
        assertFalse(videoItem.isValid)
        assertNull(videoItem.url)
        assertNull(videoItem.description)
        assertNull(videoItem.logo)
        assertEquals(ScreenSaverVideoItem.DEFAULT_DURATION_MS, videoItem.durationInMs)
    }

    @Test
    fun given_serializedItemsCollection_when_deserialize_then_collectionsAreEqual() {
        // serialize items collection
        val imageItem =
            ScreenSaverImageItem("imageUrl", "imageDescription", "imageLogo", 45000)
        val videoItem =
            ScreenSaverVideoItem("videoUrl", "videoDescription", "videoLogo", 60000)
        val collection = ScreenSaverItemsCollection(listOf(imageItem, videoItem))
        val serializedCollection = screenSaverGson.toJson(collection)

        // deserialize
        val deserializedCollection: ScreenSaverItemsCollection =
            screenSaverGson.fromJson(serializedCollection, ScreenSaverItemsCollection::class.java)

        // compare collections
        val deserializedImageItem = deserializedCollection.next as ScreenSaverImageItem
        assertThat(deserializedImageItem).isEqualToComparingFieldByField(imageItem)
        val deserializedVideoItem = deserializedCollection.next as ScreenSaverVideoItem
        assertThat(deserializedVideoItem).isEqualToComparingFieldByField(videoItem)
    }

    @Test
    fun given_serializedItemsList_when_deserialize_then_listsAreEqual() {
        // serialize items list
        val imageItem =
            ScreenSaverImageItem("imageUrl", "imageDescription", "imageLogo", 45000)
        val videoItem =
            ScreenSaverVideoItem("videoUrl", "videoDescription", "videoLogo", 60000)
        val itemsList = listOf(imageItem, videoItem)
        val serializedList = screenSaverGson.toJson(itemsList)

        // deserialize
        val deserializedList: List<ScreenSaverItem> =
            screenSaverGson.fromJson<List<ScreenSaverItem>>(
                serializedList,
                object : TypeToken<List<ScreenSaverItem>>() {}.type
            )

        // compare lists
        val deserializedImageItem = deserializedList[0] as ScreenSaverImageItem
        assertThat(deserializedImageItem).isEqualToComparingFieldByField(imageItem)
        val deserializedVideoItem = deserializedList[1] as ScreenSaverVideoItem
        assertThat(deserializedVideoItem).isEqualToComparingFieldByField(videoItem)
    }

    @Test
    fun given_imageItem_when_serializeAndDeserialize_then_fieldsAreTheSame() {
        // create image item
        val imageItem =
            ScreenSaverImageItem("imageUrl", "imageDescription", "imageLogo", 45000)

        // serialize and deserialize item
        val serializedImageItem = screenSaverGson.toJson(imageItem)
        val deserializedImageItem =
            screenSaverGson.fromJson(
                serializedImageItem,
                ScreenSaverItem::class.java
            ) as ScreenSaverImageItem

        // compare with original
        assertThat(deserializedImageItem).isEqualToComparingFieldByField(imageItem)
    }

    @Test
    fun given_videoItem_when_serializeAndDeserialize_then_fieldsAreTheSame() {
        // create video item
        val videoItem =
            ScreenSaverVideoItem("videoUrl", "videoDescription", "videoLogo", 60000)

        // serialize and deserialize item
        val serializedVideoItem = screenSaverGson.toJson(videoItem)
        val deserializedVideoItem =
            screenSaverGson.fromJson(
                serializedVideoItem,
                ScreenSaverItem::class.java
            ) as ScreenSaverVideoItem

        // compare with original
        assertThat(deserializedVideoItem).isEqualToComparingFieldByField(videoItem)
    }

    @Test
    fun given_diskImageItem_when_serializeAndDeserialize_then_fieldsAreTheSame() {
        // create disk image item from mocked file
        val mockedImageFile = mock(File::class.java)
        whenever(mockedImageFile.path).thenReturn("testImagePath")
        whenever(mockedImageFile.lastModified()).thenReturn(12345)
        whenever(mockedImageFile.length()).thenReturn(6789)
        val imageMediaItem = ScreenSaverDiskItem(mockedImageFile)
        val imageItem =
            ScreenSaverImageItem("imageUrl", "imageDescription", "imageLogo", 45000)
        imageMediaItem.screenSaverInfo = imageItem

        // serialize and deserialize disk item
        val serializedImageMediaItem =
            screenSaverGson.toJson(imageMediaItem as ScreenSaverMediaItem)
        val deserializedImageMediaItem =
            screenSaverGson.fromJson(serializedImageMediaItem, ScreenSaverDiskItem::class.java)

        // compare items to the original
        assertThat(deserializedImageMediaItem).isEqualToComparingFieldByField(imageMediaItem)
    }

    @Test
    fun given_diskVideoItem_when_serializeAndDeserialize_then_fieldsAreTheSame() {
        // create disk image item from mocked file
        val mockVideoFile = mock(File::class.java)
        whenever(mockVideoFile.path).thenReturn("testVideoPath")
        whenever(mockVideoFile.lastModified()).thenReturn(2468)
        whenever(mockVideoFile.length()).thenReturn(13579)
        val videoMediaItem = ScreenSaverDiskItem(mockVideoFile)
        val videoItem =
            ScreenSaverImageItem("videoUrl", "videoDescription", "videoLogo", 60000)
        videoMediaItem.screenSaverInfo = videoItem

        // serialize and deserialize disk item
        val video = screenSaverGson.toJson(videoMediaItem as ScreenSaverMediaItem)
        val deserializedVideoMediaItem = screenSaverGson.fromJson(video, ScreenSaverDiskItem::class.java)

        // compare items to the original
        assertThat(deserializedVideoMediaItem).isEqualToComparingFieldByField(videoMediaItem)
    }

    @Test
    fun given_mediaItemsList_when_serializeAndDeserialize_then_listsAreEqual() {
        // create media items list
        val mockImageFile = mock(File::class.java)
        whenever(mockImageFile.path).thenReturn("testImagePath")
        whenever(mockImageFile.lastModified()).thenReturn(12345)
        whenever(mockImageFile.length()).thenReturn(6789)
        val imageMediaItem = ScreenSaverDiskItem(mockImageFile)
        val videoMediaItem = ScreenSaverDiskItem(mockImageFile)
        val imageItem =
            ScreenSaverImageItem("imageUrl", "imageDescription", "imageLogo", 45000)
        val videoItem =
            ScreenSaverImageItem("videoUrl", "videoDescription", "videoLogo", 60000)
        imageMediaItem.screenSaverInfo = imageItem
        videoMediaItem.screenSaverInfo = videoItem
        val mediaItemsList =
            listOf(imageMediaItem as ScreenSaverMediaItem, videoMediaItem as ScreenSaverMediaItem)

        // serialize and deserialize media items list
        val serializedMediaItemsList = screenSaverGson.toJson(mediaItemsList)
        val deserializedMediaItemsList = screenSaverGson.fromJson<List<ScreenSaverDiskItem>>(
            serializedMediaItemsList,
            object : TypeToken<List<ScreenSaverDiskItem>>() {}.type
        )

        // compare items to original
        val deserializedImageMediaItem = deserializedMediaItemsList[0]
        assertThat(deserializedImageMediaItem).isEqualToComparingFieldByField(imageMediaItem)
        val deserializedVideoMediaItem = deserializedMediaItemsList[1]
        assertThat(deserializedVideoMediaItem).isEqualToComparingFieldByField(videoMediaItem)
    }
}
