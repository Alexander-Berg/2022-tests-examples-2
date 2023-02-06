package ru.yandex.quasar.app.screensaver.screenSaverHelpers

import androidx.test.ext.junit.runners.AndroidJUnit4
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import org.assertj.core.api.Assertions.assertThat
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import ru.yandex.quasar.app.screensaver.screenSaverItems.ScreenSaverItem
import ru.yandex.quasar.app.screensaver.suggests.ScreenSaverSuggest
import ru.yandex.quasar.app.screensaver.suggests.ScreenSaverSuggestsCollection

@RunWith(AndroidJUnit4::class)
@Config(manifest = Config.NONE)
class ScreenSaverSuggestsLoaderTest {
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
    fun given_recommendationConfig_when_deserialize_then_suggestIsCorrect() {
        val suggestsConfig = "{\n" +
                "    \"items\": [\n" +
                "        {\n" +
                "            \"id\": \"onboarding_get_weather_today\",\n" +
                "            \"activation\": \"Какая сегодня погода\",\n" +
                "            \"description\": \"Одевайтесь по погоде.\",\n" +
                "            \"logo_avatar_id\": \"1535439/onboard_Wheather\",\n" +
                "            \"logo_prefix\": \"paskills\",\n" +
                "            \"look\": \"internal\",\n" +
                "            \"name\": \"Какая сегодня погода\",\n" +
                "            \"logo_bg_color\": \"#919cb5\",\n" +
                "            \"logo_bg_image_quasar_id\": \"1525540/quasar_logo_1_poi\",\n" +
                "            \"logo_fg_round_image_url\": \"https://avatars.mds.yandex.net/get-dialogs/1535439/onboard_Wheather/mobile-logo-round-x2\",\n" +
                "            \"logo_amelie_bg_url\": \"https://avatars.mds.yandex.net/get-dialogs/1017510/tallLogo1/logo-bg-image-tall-x2\",\n" +
                "            \"search_app_card_item_text\": \"«Алиса, какая сегодня погода»\"\n" +
                "        }\n" +
                "    ],\n" +
                "    \"recommendation_type\": \"editorial#\",\n" +
                "    \"recommendation_source\": \"station_screensaver\"\n" +
                "}"
        val collection =
            screenSaverGson.fromJson(suggestsConfig, ScreenSaverSuggestsCollection::class.java)
        assertTrue(collection.hasNext)
        val item = collection.next
        assertNotNull(item)
        if (item == null) {
            return
        }
        assertEquals("onboarding_get_weather_today", item.id)
        assertEquals("Алиса, какая сегодня погода", item.getText("Алиса"))
        assertEquals("Яндекс, какая сегодня погода", item.getText("Яндекс"))
        assertEquals("Другой споттер, какая сегодня погода", item.getText("Другой споттер"))
    }

    @Test
    fun given_configWithoutActivationField_when_deserialize_then_suggestTextIsSpotter() {
        val suggestsConfig = "{\"id\": \"onboarding_get_weather_today\"}"
        val item = screenSaverGson.fromJson(suggestsConfig, ScreenSaverSuggest::class.java)
        assertNotNull(item)
        if (item == null) {
            return
        }
        assertEquals("onboarding_get_weather_today", item.id)
        assertEquals("Алиса", item.getText("Алиса"))
        assertEquals("Яндекс", item.getText("Яндекс"))
        assertEquals("Другой споттер", item.getText("Другой споттер"))
    }

    @Test
    fun given_suggestItem_when_getTextWithoutSpotter_then_suggestIsEmpty() {
        val item = ScreenSaverSuggest("onboarding_get_weather_today", "Какая сегодня погода")
        assertEquals("", item.getText(""))
    }

    @Test
    fun given_configWithNullFields_when_deserialize_then_suggestTextIsSpotter() {
        val suggestsConfig = "{\"id\":null, \"activation\": null}"
        val item = screenSaverGson.fromJson(suggestsConfig, ScreenSaverSuggest::class.java)
        assertNotNull(item)
        if (item == null) {
            return
        }
        assertEquals(null, item.id)
        assertEquals("Алиса", item.getText("Алиса"))
        assertEquals("Яндекс", item.getText("Яндекс"))
        assertEquals("Другой споттер", item.getText("Другой споттер"))
    }

    @Test
    fun given_suggestsCollection_when_getNext_then_itemIsCorrect() {
        val item1 = ScreenSaverSuggest("onboarding_get_weather_today", "Какая сегодня погода")
        val item2 = ScreenSaverSuggest("games_onboarding_cities", "Давай сыграем в города")
        val collection = ScreenSaverSuggestsCollection(listOf(item1, item2))

        assertTrue(collection.hasNext)
        val nextItem1 = collection.next
        val text1 = nextItem1!!.getText("Алиса")
        assertTrue(nextItem1.id == item1.id || nextItem1.id == item2.id)
        assertTrue(text1 == item1.getText("Алиса") || text1 == item2.getText("Алиса"))

        assertTrue(collection.hasNext)
        val nextItem2 = collection.next
        val text2 = nextItem2!!.getText("Алиса")
        assertTrue(nextItem2.id == item1.id || nextItem2.id == item2.id)
        assertTrue(text2 == item1.getText("Алиса") || text2 == item2.getText("Алиса"))
    }

    @Test
    fun given_suggestsCollection_when_getNextFewTimes_then_getRandomIsCorrect() {
        val item1 = ScreenSaverSuggest("onboarding_get_weather_today", "Какая сегодня погода")
        val item2 = ScreenSaverSuggest("games_onboarding_cities", "Давай сыграем в города")
        val collection = ScreenSaverSuggestsCollection(listOf(item1, item2))

        assertNotNull(collection.next)
        assertNotNull(collection.next)

        assertFalse(collection.hasNext)
        assertNull(collection.next)

        val randomItem = collection.getRandomItem()
        val text = randomItem!!.getText("Алиса")
        assertTrue(randomItem.id == item1.id || randomItem.id == item2.id)
        assertTrue(text == item1.getText("Алиса") || text == item2.getText("Алиса"))
    }

    @Test
    fun given_serializedSuggest_when_deserialize_then_itemsAreEqual() {
        val suggest = ScreenSaverSuggest("onboarding_get_weather_today", "Какая сегодня погода")
        val serializedSuggest = screenSaverGson.toJson(suggest)
        val deserializedSuggest =
            screenSaverGson.fromJson(serializedSuggest, ScreenSaverSuggest::class.java)

        assertEquals(
            "{\"id\":\"onboarding_get_weather_today\",\"activation\":\"Какая сегодня погода\"}",
            serializedSuggest
        )
        assertThat(deserializedSuggest).isEqualToComparingFieldByField(suggest)
    }

    @Test
    fun given_suggestWithNullFields_when_serializeAndDeserialize_then_itemsAreEqual() {
        val suggest = ScreenSaverSuggest(null, null)
        val serializedSuggest = screenSaverGson.toJson(suggest)
        val deserializedSuggest =
            screenSaverGson.fromJson(serializedSuggest, ScreenSaverSuggest::class.java)

        assertThat(deserializedSuggest).isEqualToComparingFieldByField(suggest)
    }

    @Test
    fun given_null_when_serializeAndDeserialize_then_itemIsNull() {
        val suggest: ScreenSaverSuggest? = null
        val serializedSuggest = screenSaverGson.toJson(suggest)
        val deserializedSuggest =
            screenSaverGson.fromJson(serializedSuggest, ScreenSaverSuggest::class.java)

        assertEquals("null", serializedSuggest)
        assertNull(deserializedSuggest)
    }
}
