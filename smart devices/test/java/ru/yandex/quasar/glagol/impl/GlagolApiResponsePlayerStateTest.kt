package ru.yandex.quasar.glagol.impl

import org.json.JSONException
import org.junit.Assert
import org.junit.Test
import ru.yandex.quasar.glagol.conversation.model.RepeatMode
import java.io.IOException

class GlagolApiResponsePlayerStateTest {

    @Test
    fun parsePlayerState() {
        val player = ConversationImpl.getReceivedMessageWrapper(
            GlagolApiResponseTest.getTestJson("/playerStateOnlyFull.json"), GsonFactory.receievedMessagesParser()
        ).state.playerState!!

        Assert.assertNotNull(player)

        Assert.assertEquals(player.playerType, "player-type-value")
        Assert.assertFalse(player.isHasNext)
        Assert.assertFalse(player.hasPlay())
        Assert.assertFalse(player.isHasProgressBar)
        Assert.assertFalse(player.isHasPrev)
        Assert.assertTrue(player.hasPause())
        Assert.assertFalse(player.shouldShowPlayer())
        Assert.assertEquals("unknown", player.type)
        Assert.assertTrue(49 < player.progress!!)
        Assert.assertTrue(51 > player.progress!!)
        Assert.assertEquals("321", player.id)
        Assert.assertEquals("artist", player.subtitle)
        Assert.assertEquals("track", player.title)
        Assert.assertTrue(99.9 < player.duration!!)
        Assert.assertTrue(100.1 > player.duration!!)
        Assert.assertEquals("live stream", player.liveStreamText)
        Assert.assertEquals("album", player.playlistType)
        Assert.assertEquals("playlist-id", player.playlistId)
        Assert.assertEquals("playlist-description", player.playlistDescription)
    }

    @Test
    fun parsePlayerState_variant2() {
        val player = ConversationImpl.getReceivedMessageWrapper(
            GlagolApiResponseTest.getTestJson("/playerStateOnlyFull_variant2.json"), GsonFactory.receievedMessagesParser()
        ).state.playerState!!

        Assert.assertNotNull(player)

        Assert.assertEquals(player.playerType, "player-type-value-2")
        Assert.assertTrue(player.isHasNext)
        Assert.assertTrue(player.hasPlay())
        Assert.assertTrue(player.isHasProgressBar)
        Assert.assertTrue(player.isHasPrev)
        Assert.assertFalse(player.hasPause())
        Assert.assertTrue(player.shouldShowPlayer())
        Assert.assertEquals("track", player.type)
        Assert.assertTrue(player.progress!!.compareTo(0.0) == 0)
        Assert.assertEquals("123", player.id)
        Assert.assertEquals("subtitle-value", player.subtitle)
        Assert.assertEquals("title-value", player.title)
        Assert.assertTrue(199.5 < player.duration!!)
        Assert.assertTrue(200.5 > player.duration!!)
        Assert.assertEquals("live-stream-text", player.liveStreamText)
        Assert.assertEquals("playlist", player.playlistType)
        Assert.assertEquals("playlist-id-2", player.playlistId)
        Assert.assertEquals("playlist-description-2", player.playlistDescription)
    }

    @Test
    fun parseNulledPlayerState() {
        val player = ConversationImpl.getReceivedMessageWrapper(
            GlagolApiResponseTest.getTestJson("/playerStateOnlyNulled.json"), GsonFactory.receievedMessagesParser()
        ).state.playerState!!

        Assert.assertNull(player.entityInfo)
        Assert.assertNull(player.extra)
        Assert.assertNull(player.playerType)
        Assert.assertNull(player.playlistId)
        Assert.assertNull(player.playlistType)
        Assert.assertNull(player.playlistDescription)
    }

    @Test
    fun parseEntityInfo() {
        val info = ConversationImpl.getReceivedMessageWrapper(
            GlagolApiResponseTest.getTestJson("/playerStateOnlyFull.json"), GsonFactory.receievedMessagesParser()
        ).state.playerState!!.entityInfo!!

        Assert.assertNotNull(info)
        Assert.assertTrue(info.isShuffled()!!)
        Assert.assertEquals(info.getId(), "12345")
        Assert.assertEquals(info.getType(), "Album")
        Assert.assertEquals(info.getDescription(), "asdfkj")
        Assert.assertNotNull(info.getPrev())
        Assert.assertEquals(info.getPrev()!!.getId(), "34566")
        Assert.assertEquals(info.getPrev()!!.getType(), "Track")
        Assert.assertNotNull(info.getNext())
        Assert.assertEquals(info.getNext()!!.getId(), "95736")
        Assert.assertEquals(info.getNext()!!.getType(), "Track")
        Assert.assertEquals(info.getRepeatMode(), RepeatMode.None)
    }

    @Test
    fun parseEntityInfo_variant2() {
        val info = ConversationImpl.getReceivedMessageWrapper(
            GlagolApiResponseTest.getTestJson("/playerStateOnlyFull_variant2.json"), GsonFactory.receievedMessagesParser()
        ).state.playerState!!.entityInfo!!

        Assert.assertNotNull(info)
        Assert.assertFalse(info.isShuffled()!!)
        Assert.assertEquals(info.getId(), "123456")
        Assert.assertEquals(info.getType(), "Playlist")
        Assert.assertEquals(info.getDescription(), "qwerty")
        Assert.assertNotNull(info.getPrev())
        Assert.assertEquals(info.getPrev()!!.getId(), "123")
        Assert.assertEquals(info.getPrev()!!.getType(), "Type-value-0")
        Assert.assertNotNull(info.getNext())
        Assert.assertEquals(info.getNext()!!.getId(), "321")
        Assert.assertEquals(info.getNext()!!.getType(), "Type-value-2")
        Assert.assertEquals(info.getRepeatMode(), RepeatMode.All)
    }

    @Test
    @Throws(IOException::class, JSONException::class)
    fun parsePlayerStateExtraFields() {
        val wrapper = ConversationImpl.getReceivedMessageWrapper(
            GlagolApiResponseTest.getTestJson("/playerStateOnlyFull.json"),
            GsonFactory.receievedMessagesParser()
        )
        val message = MessageImpl(
            wrapper.id, wrapper.sentTime,
            wrapper.state, wrapper.status, wrapper.requestId, wrapper.extra,
            wrapper.supportedFeatures, wrapper.vinsResponse, wrapper.errorCode,
            wrapper.errorText, wrapper.errorTextLang
        )
        val extras = message.state.playerState!!
            .extra
        Assert.assertNotNull(extras)
        Assert.assertEquals("req-id-value", extras["requestId"])
        Assert.assertEquals("firmware-version", extras["softwareVersion"])
    }

}
