package ru.yandex.quasar.app.video.video_settings

import android.graphics.Point
import android.view.View
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.shadows.ShadowLogger

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowLogger::class], instrumentedPackages = ["ru.yandex.quasar.util"])
class VideoSettingsFocusManagerTest {

    @Test
    fun given_correctFocus_when_fullColumnListBuilt_then_notOutOfBounds() {
        val focusManager = VideoSettingsFocusManager()
        val audioTracks = listOf(
                VideoSettingsElement("", "", 0, null, false, false),
                VideoSettingsElement("", "", 1, null, true, false)
        )

        val languages = listOf(
                VideoSettingsElement("", "", 0, null, false, false),
                VideoSettingsElement("", "", 1, null, false, false),
                VideoSettingsElement("", "", 2, null, false, false)
        )

        focusManager.setAvailableStreams(audioTracks, languages)

        assert(focusManager.hasFocus)
        assertEquals(Point(0, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_UP)
        focusManager.focusSearch(View.FOCUS_UP)
        assertEquals(Point(0, 0), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_DOWN)
        focusManager.focusSearch(View.FOCUS_DOWN)
        assertEquals(Point(0, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_LEFT)
        assertEquals(Point(0, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_RIGHT)
        focusManager.focusSearch(View.FOCUS_RIGHT)
        assertEquals(Point(1, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_DOWN)
        focusManager.focusSearch(View.FOCUS_DOWN)
        assertEquals(Point(1, 2), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_LEFT)
        assertEquals(Point(0, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_RIGHT)
        focusManager.focusSearch(View.FOCUS_UP)
        assertEquals(Point(1, 0), focusManager.currentFocus)
    }

    @Test
    fun given_correctFocus_when_rightPartBuilt_then_notOutOfBounds() {
        val focusManager = VideoSettingsFocusManager()
        val audioTracks = emptyList<VideoSettingsElement>()

        val languages = listOf(
                VideoSettingsElement("", "", 0, null, true, false),
                VideoSettingsElement("", "", 1, null, false, false),
                VideoSettingsElement("", "", 2, null, false, false)
        )

        focusManager.setAvailableStreams(audioTracks, languages)

        assert(focusManager.hasFocus)
        assertEquals(Point(1, 0), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_LEFT)
        assertEquals(Point(1, 0), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_RIGHT)
        assertEquals(Point(1, 0), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_DOWN)
        focusManager.focusSearch(View.FOCUS_DOWN)
        focusManager.focusSearch(View.FOCUS_DOWN)
        assertEquals(Point(1, 2), focusManager.currentFocus)
    }

    @Test
    fun given_correctFocus_when_leftPartBuilt_then_notOutOfBounds() {
        val focusManager = VideoSettingsFocusManager()
        val audioTracks = listOf(
                VideoSettingsElement("", "", 0, null, false, false),
                VideoSettingsElement("", "", 1, null, true, false)
        )

        val languages = emptyList<VideoSettingsElement>()

        focusManager.setAvailableStreams(audioTracks, languages)

        assert(focusManager.hasFocus)
        assertEquals(Point(0, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_RIGHT)
        assertEquals(Point(0, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_LEFT)
        assertEquals(Point(0, 1), focusManager.currentFocus)
    }

    @Test
    fun given_focusMissing_when_columnListCleared_then_notOutOfBounds() {
        val focusManager = VideoSettingsFocusManager()
        val audioTracks = emptyList<VideoSettingsElement>()
        val languages = emptyList<VideoSettingsElement>()

        focusManager.setAvailableStreams(audioTracks, languages)
        focusManager.focusSearch(View.FOCUS_RIGHT)
        focusManager.focusSearch(View.FOCUS_LEFT)
        focusManager.focusSearch(View.FOCUS_UP)
        focusManager.focusSearch(View.FOCUS_DOWN)
        assert(!focusManager.hasFocus)
    }

    @Test
    fun given_correctFocus_when_middleColumnCleared_then_notOutOfBounds() {
        val focusManager = VideoSettingsFocusManager()
        val audioTracks = listOf(
                VideoSettingsElement("", "", 0, null, false, false),
                VideoSettingsElement("", "", 1, null, true, false)
        )

        val middleEmptyList = emptyList<VideoSettingsElement>()

        val languages = listOf(
                VideoSettingsElement("", "", 0, null, false, false),
                VideoSettingsElement("", "", 1, null, false, false),
                VideoSettingsElement("", "", 2, null, false, false)
        )

        focusManager.setAvailableStreams(audioTracks, middleEmptyList, languages)

        assert(focusManager.hasFocus)
        assertEquals(Point(0, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_RIGHT)
        assertEquals(Point(2, 1), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_DOWN)
        focusManager.focusSearch(View.FOCUS_DOWN)
        assertEquals(Point(2, 2), focusManager.currentFocus)

        focusManager.focusSearch(View.FOCUS_LEFT)
        assertEquals(Point(0, 1), focusManager.currentFocus)
    }
}
