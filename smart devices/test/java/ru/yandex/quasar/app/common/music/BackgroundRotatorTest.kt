package ru.yandex.quasar.app.common.music

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class BackgroundRotatorTest {
    @Test
    fun when_trackChanges_then_backgroundChangesToo() {
        // Given
        val backs = listOf(1,2,3,4,5)
        val backgroundRotator = BackgroundRotator(backs)

        // When
        val track1 = TrackMetaInfo("title1", "artist1", "album1", 424242, null)
        val back1 = backgroundRotator.rotateIfNecessary(track1)

        val track2 = TrackMetaInfo("title2", "artist2", "album2", 535353, null)
        val back2 = backgroundRotator.rotateIfNecessary(track2)


        // Then
        assertNotEquals(back1, back2)
        assertTrue(backs.contains(back1))
        assertTrue(backs.contains(back2))
    }

    @Test
    fun when_switchingBackgroundsSeveralTimes_then_backgroundsListIsCycled() {
        // Given
        val backs = listOf(1,2)
        val backgroundRotator = BackgroundRotator(backs)

        // When
        val track1 = TrackMetaInfo("title1", "artist1", "album1", 424242, null)
        val back1 = backgroundRotator.rotateIfNecessary(track1)

        val track2 = TrackMetaInfo("title2", "artist2", "album2", 535353, null)
        val back2 = backgroundRotator.rotateIfNecessary(track2)

        val track3 = TrackMetaInfo("title3", "artist3", "album3", 646464, null)
        val back3 = backgroundRotator.rotateIfNecessary(track3)

        // Then
        assertNotEquals(back1, back2)
        assertEquals(back1, back3)
    }

    @Test
    fun when_switchToPastTrack_then_backgroundStillChanges() {
        // Given
        val backs = listOf(1, 2, 3)
        val backgroundRotator = BackgroundRotator(backs)

        // When
        val track1 = TrackMetaInfo("title1", "artist1", "album1", 424242, null)
        val back1 = backgroundRotator.rotateIfNecessary(track1)

        val track2 = TrackMetaInfo("title2", "artist2", "album2", 535353, null)
        val back2 = backgroundRotator.rotateIfNecessary(track2)

        val back3 = backgroundRotator.rotateIfNecessary(track1)

        // Then
        assertNotEquals(back1, back2)
        assertNotEquals(back1, back3)
        assertNotEquals(back2, back3)
    }

    @Test
    fun when_trackIsNotChanged_then_backgroundIsNotChangingToo() {
        // Given
        val backs = listOf(1, 2, 3)
        val backgroundRotator = BackgroundRotator(backs)

        // When
        val track1 = TrackMetaInfo("title1", "artist1", "album1", 424242, null)
        val back1 = backgroundRotator.rotateIfNecessary(track1)
        val back2 = backgroundRotator.rotateIfNecessary(track1)

        // Then
        assertEquals(back1, back2)
    }

    @Test
    fun when_onlyTrackLengthIsChanged_then_backgroundIsNotChanging() {
        // Given
        val backs = listOf(1, 2, 3)
        val backgroundRotator = BackgroundRotator(backs)

        // When
        val track1 = TrackMetaInfo("title1", "artist1", "album1", 424242, null)
        val back1 = backgroundRotator.rotateIfNecessary(track1)

        val track2 = TrackMetaInfo("title1", "artist1", "album1", 999999, null)
        val back2 = backgroundRotator.rotateIfNecessary(track2)

        // Then
        assertEquals(back1, back2)
    }
}
