package ru.yandex.quasar.app.utils;

import android.content.Context;

import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.mockito.invocation.InvocationOnMock;
import org.mockito.stubbing.Answer;
import org.robolectric.annotation.Config;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

import ru.yandex.quasar.app.R;
import ru.yandex.quasar.view.SuggestItem;
import ru.yandex.quasar.app.main.SuggestUtils;
import ru.yandex.quasar.protobuf.ModelObjects;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@RunWith(AndroidJUnit4.class)
@Config(manifest = Config.NONE)
public class SuggestUtilsTest {
    @Mock
    private Context mockApplicationContext;

    private HashMap<Integer, String> initDescriptionMock() {
        HashMap<Integer, String> descriptionStrings = new HashMap<>();
        descriptionStrings.put(R.string.help, "Помощь");
        descriptionStrings.put(R.string.to_home, "Домой");
        descriptionStrings.put(R.string.seasons_list, "Список сезонов");
        descriptionStrings.put(R.string.watch_movie, "Смотреть фильм");
        descriptionStrings.put(R.string.watch, "Смотреть");
        descriptionStrings.put(R.string.buy, "Купить");
        descriptionStrings.put(R.string.watch_first, "Смотреть с начала");
        descriptionStrings.put(R.string.authorize, "Авторизоваться");
        descriptionStrings.put(R.string.watch_trailer, "Смотреть трейлер");

        MockitoAnnotations.initMocks(this);

        for (Integer key : descriptionStrings.keySet()) {
            when(mockApplicationContext.getString(key)).thenReturn(descriptionStrings.get(key));
        }

        return descriptionStrings;
    }

    private HashMap<Integer, String> initPaymentMock() {
        HashMap<Integer, String> descriptionStrings = new HashMap<>();
        descriptionStrings.put(R.string.help, "Помощь");
        descriptionStrings.put(R.string.to_home, "Домой");

        MockitoAnnotations.initMocks(this);

        for (Integer key : descriptionStrings.keySet()) {
            when(mockApplicationContext.getString(key)).thenReturn(descriptionStrings.get(key));
        }

        return descriptionStrings;
    }

    private HashMap<Integer, String> initVideoListMock() {
        HashMap<Integer, String> descriptionStrings = new HashMap<>();
        descriptionStrings.put(R.string.help, "Помощь");
        descriptionStrings.put(R.string.to_home, "Домой");
        descriptionStrings.put(R.string.to_begin, "В начало");
        descriptionStrings.put(R.string.watch_movie, "Смотреть фильм");
        descriptionStrings.put(R.string.watch, "Смотреть");
        descriptionStrings.put(R.string.buy, "Купить");
        descriptionStrings.put(R.string.to_end, "В конец");
        descriptionStrings.put(R.string.watch_by_name, "Запусти %s");
        descriptionStrings.put(R.string.watch_by_number, "Включи номер %s");

        MockitoAnnotations.initMocks(this);

        for (Integer key : descriptionStrings.keySet()) {
            when(mockApplicationContext.getString(key)).thenReturn(descriptionStrings.get(key));
        }

        when(mockApplicationContext.getString(anyInt(), anyString())).thenAnswer((Answer<String>) invocation -> {
            String resource = descriptionStrings.get(invocation.getArgument(0));
            if (resource == null) {
                return null;
            }
            return String.format(resource, new Object[]{invocation.getArgument(1)});
        });

        return descriptionStrings;
    }

    @Test
    public void testPaymentSuggests() {
        HashMap<Integer, String> resources = initPaymentMock();
        List<SuggestItem> suggests = SuggestUtils.getPaymentScreenSuggets(mockApplicationContext);
        assertEquals(2, suggests.size());
        assertEquals(resources.get(R.string.to_home), suggests.get(0).text);
        assertEquals(resources.get(R.string.help), suggests.get(1).text);
    }

    @Test
    public void testDescriptionSuggestsEmptyItem() {
        HashMap<Integer, String> resources = initDescriptionMock();
        ModelObjects.MediaItem mediaItem = ModelObjects.MediaItem.newBuilder().build();
        List<String> expectedSuggests = Arrays.asList(
                resources.get(R.string.help),
                resources.get(R.string.to_home),
                resources.get(R.string.buy));

        List<SuggestItem> suggests = SuggestUtils.getDescriptionSuggests(mockApplicationContext, mediaItem, 4);
        assertEquals(3, suggests.size());
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));
            assertFalse(item.hasImage());
            assertEquals(-1, item.imageId);
        }
    }

    @Test
    public void testDescriptionSuggestsTvItem() {
        HashMap<Integer, String> resources = initDescriptionMock();
        ModelObjects.MediaItem mediaItem = ModelObjects.MediaItem.newBuilder()
                .setType(ModelObjects.MediaItem.Type.TV_SHOW)
                .build();
        List<String> expectedSuggests = Arrays.asList(
                resources.get(R.string.help),
                resources.get(R.string.to_home),
                resources.get(R.string.seasons_list),
                resources.get(R.string.buy));

        List<SuggestItem> suggests = SuggestUtils.getDescriptionSuggests(mockApplicationContext, mediaItem, 4);
        assertEquals(4, suggests.size());
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));
            assertFalse(item.hasImage());
            assertEquals(-1, item.imageId);
        }
    }

    @Test
    public void testDescriptionSuggestsKinopoiskItem() {
        HashMap<Integer, String> resources = initDescriptionMock();
        ModelObjects.ProviderInfo providerInfo = ModelObjects.ProviderInfo.newBuilder()
                .setProvider(ModelObjects.Provider.KINOPOISK)
                .setAvailable(true)
                .build();
        ModelObjects.MediaItem mediaItem = ModelObjects.MediaItem.newBuilder()
                .setType(ModelObjects.MediaItem.Type.MOVIE)
                .addProviderInfo(providerInfo)
                .build();
        List<String> expectedSuggests = Arrays.asList(
                resources.get(R.string.help),
                resources.get(R.string.to_home),
                resources.get(R.string.watch_movie),
                resources.get(R.string.buy));

        List<SuggestItem> suggests = SuggestUtils.getDescriptionSuggests(mockApplicationContext, mediaItem, 4);
        assertEquals(4, suggests.size());
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));

            if (item.text.equals(resources.get(R.string.watch_movie))) {
                assertTrue(item.hasImage());
                assertEquals(R.drawable.kinopoisk, item.imageId);
            } else {
                assertFalse(item.hasImage());
                assertEquals(-1, item.imageId);
            }
        }
    }

    @Test
    public void testDescriptionSuggestsUnauthorizedItem() {
        HashMap<Integer, String> resources = initDescriptionMock();
        ModelObjects.MediaItem mediaItem = ModelObjects.MediaItem.newBuilder()
                .setUnauthorized(true)
                .build();
        List<String> expectedSuggests = Arrays.asList(
                resources.get(R.string.help),
                resources.get(R.string.to_home),
                resources.get(R.string.authorize),
                resources.get(R.string.buy));

        List<SuggestItem> suggests = SuggestUtils.getDescriptionSuggests(mockApplicationContext, mediaItem, 4);
        assertEquals(4, suggests.size());
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));
            assertFalse(item.hasImage());
            assertEquals(-1, item.imageId);
        }
    }

    @Test
    public void testDescriptionSuggestsContinueWatchItem() {
        HashMap<Integer, String> resources = initDescriptionMock();
        ModelObjects.MediaItem mediaItem = ModelObjects.MediaItem.newBuilder()
                .setAvailable(true)
                .setProgressPercents(10)
                .build();
        List<String> expectedSuggests = Arrays.asList(
                resources.get(R.string.help),
                resources.get(R.string.to_home),
                resources.get(R.string.watch_first),
                resources.get(R.string.buy));

        List<SuggestItem> suggests = SuggestUtils.getDescriptionSuggests(mockApplicationContext, mediaItem, 4);
        assertEquals(4, suggests.size());
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));
            assertFalse(item.hasImage());
            assertEquals(-1, item.imageId);
        }
    }

    @Test
    public void testDescriptionSuggestsTrailerItem() {
        HashMap<Integer, String> resources = initDescriptionMock();
        ModelObjects.MediaItem mediaItem = ModelObjects.MediaItem.newBuilder()
                .setTrailerAvailable(true)
                .build();
        List<String> expectedSuggests = Arrays.asList(
                resources.get(R.string.help),
                resources.get(R.string.to_home),
                resources.get(R.string.watch_trailer),
                resources.get(R.string.buy));

        List<SuggestItem> suggests = SuggestUtils.getDescriptionSuggests(mockApplicationContext, mediaItem, 4);
        assertEquals(4, suggests.size());
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));
            assertFalse(item.hasImage());
            assertEquals(-1, item.imageId);
        }
    }

    @Test
    public void testDescriptionSuggestsRandomItem() {
        HashMap<Integer, String> resources = initDescriptionMock();
        ModelObjects.MediaItem mediaItem = ModelObjects.MediaItem.newBuilder()
                .setType(ModelObjects.MediaItem.Type.TV_SHOW)
                .setAvailable(true)
                .addProviderInfo(ModelObjects.ProviderInfo.newBuilder().setAvailable(true))
                .setTrailerAvailable(true)
                .build();
        List<String> expectedSuggests = new ArrayList<>(resources.values());

        List<SuggestItem> suggests = SuggestUtils.getDescriptionSuggests(mockApplicationContext, mediaItem, 4);
        assertEquals(4, suggests.size());
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));
            assertFalse(item.hasImage());
            assertEquals(-1, item.imageId);
        }
    }

    @Test
    public void testVideoListSuggestsEmptyList() {
        HashMap<Integer, String> resources = initVideoListMock();
        List<ModelObjects.MediaItem> items = new ArrayList<>();

        List<SuggestItem> suggests = SuggestUtils.getSuggestsForVideoList(mockApplicationContext, 0, 0, 0, 4, Integer.MAX_VALUE, items);
        assertEquals(1, suggests.size());
        assertEquals(resources.get(R.string.help), suggests.get(0).text);
        assertFalse(suggests.get(0).hasImage());
        assertEquals(-1, suggests.get(0).imageId);
    }

    @Test
    public void testVideoListSuggestsAtEnd() {
        HashMap<Integer, String> resources = initVideoListMock();
        List<ModelObjects.MediaItem> items = new ArrayList<>();

        List<SuggestItem> suggests = SuggestUtils.getSuggestsForVideoList(mockApplicationContext, 1, 5, 6, 4, Integer.MAX_VALUE, items);
        assertEquals(2, suggests.size());
        assertEquals(resources.get(R.string.to_begin), suggests.get(0).text);
        assertEquals(resources.get(R.string.help), suggests.get(1).text);
        assertFalse(suggests.get(0).hasImage());
        assertFalse(suggests.get(1).hasImage());
        assertEquals(-1, suggests.get(0).imageId);
        assertEquals(-1, suggests.get(1).imageId);
    }

    @Test
    public void testVideoListSuggestsAtStart() {
        HashMap<Integer, String> resources = initVideoListMock();
        List<ModelObjects.MediaItem> items = new ArrayList<>();

        List<SuggestItem> suggests = SuggestUtils.getSuggestsForVideoList(mockApplicationContext, 0, 5, 7, 4, Integer.MAX_VALUE, items);
        assertEquals(2, suggests.size());
        assertEquals(resources.get(R.string.help), suggests.get(0).text);
        assertEquals(resources.get(R.string.to_end), suggests.get(1).text);
        assertFalse(suggests.get(0).hasImage());
        assertFalse(suggests.get(1).hasImage());
        assertEquals(-1, suggests.get(0).imageId);
        assertEquals(-1, suggests.get(1).imageId);
    }

    @Test
    public void testVideoListSuggestsInTheMiddle() {
        HashMap<Integer, String> resources = initVideoListMock();
        List<ModelObjects.MediaItem> items = new ArrayList<>();

        List<SuggestItem> suggests = SuggestUtils.getSuggestsForVideoList(mockApplicationContext, 1, 5, 7, 4, Integer.MAX_VALUE, items);
        assertEquals(3, suggests.size());
        assertEquals(resources.get(R.string.to_begin), suggests.get(0).text);
        assertEquals(resources.get(R.string.help), suggests.get(1).text);
        assertEquals(resources.get(R.string.to_end), suggests.get(2).text);
        assertFalse(suggests.get(0).hasImage());
        assertFalse(suggests.get(0).hasImage());
        assertFalse(suggests.get(2).hasImage());
        assertEquals(-1, suggests.get(0).imageId);
        assertEquals(-1, suggests.get(1).imageId);
        assertEquals(-1, suggests.get(2).imageId);
    }

    @Test
    public void testVideoListSuggestsTvItems() {
        HashMap<Integer, String> resources = initVideoListMock();
        List<ModelObjects.MediaItem> items = new ArrayList<>();
        items.add(ModelObjects.MediaItem.newBuilder()
                .setType(ModelObjects.MediaItem.Type.TV_SHOW_EPISODE)
                .setName("Test")
                .build());
        List<String> expectedSuggests = Arrays.asList(
                resources.get(R.string.help),
                String.format(resources.get(R.string.watch_by_number), 1),
                String.format(resources.get(R.string.watch_by_name), "Test"),
                resources.get(R.string.buy));

        List<SuggestItem> suggests = SuggestUtils.getSuggestsForVideoList(mockApplicationContext, 0, 0, 1, 4, Integer.MAX_VALUE, items);
        assertEquals(4, suggests.size());
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));
            assertFalse(item.hasImage());
            assertEquals(-1, item.imageId);
        }
    }

    @Test
    public void testVideoListSuggestsRandomItem() {
        HashMap<Integer, String> resources = initVideoListMock();
        List<ModelObjects.MediaItem> items = new ArrayList<>();
        items.add(ModelObjects.MediaItem.newBuilder()
                .setType(ModelObjects.MediaItem.Type.TV_SHOW_EPISODE)
                .setName("Test")
                .build());
        List<String> expectedSuggests = Arrays.asList(
                resources.get(R.string.to_begin),
                resources.get(R.string.to_end),
                resources.get(R.string.help),
                String.format(resources.get(R.string.watch_by_number), 2),
                String.format(resources.get(R.string.watch_by_name), "Test"),
                resources.get(R.string.buy));

        List<SuggestItem> suggests = SuggestUtils.getSuggestsForVideoList(mockApplicationContext, 1, 1, 3, 4, Integer.MAX_VALUE, items);
        assertEquals(4, suggests.size());
        assertEquals(resources.get(R.string.to_begin), suggests.get(0).text);
        for (SuggestItem item : suggests) {
            assertTrue(expectedSuggests.contains(item.text));
            assertFalse(item.hasImage());
            assertEquals(-1, item.imageId);
        }
        assertEquals(resources.get(R.string.to_end), suggests.get(3).text);
    }

    @Test
    public void when_maxLengthIsSet_then_longSuggestsFilteredOut() {

        HashMap<Integer, String> resources = initVideoListMock();
        List<ModelObjects.MediaItem> items = new ArrayList<>();
        char[] str = new char[50];
        Arrays.fill(str, 'A');
        items.add(ModelObjects.MediaItem.newBuilder()
                .setType(ModelObjects.MediaItem.Type.TV_SHOW_EPISODE)
                .setName(new String(str))
                .build());

        List<SuggestItem> suggests = SuggestUtils.getSuggestsForVideoList(mockApplicationContext, 0, 0, 1, 4, 32, items);
        assertEquals(3, suggests.size());
    }
}
