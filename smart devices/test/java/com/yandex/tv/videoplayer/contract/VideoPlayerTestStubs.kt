package com.yandex.tv.videoplayer.contract

import com.yandex.tv.videoplayer.PlayerContract
import com.yandex.tv.videoplayer.common.model.*
import com.yandex.tv.videoplayer.model.Playlist
import ru.yandex.video.data.dto.VideoData
import ru.yandex.video.ott.data.dto.VhVideoData

class EmptyPlayerModel : PlayerContract.Model {
    override val playlist: Playlist
        get() = Playlist()

    override suspend fun updateSuggests(video: VhVideo, rvb: String?): List<VhVideo> {
        return emptyList()
    }

    override suspend fun getVideo(contentId: String): VhVideo {
        return VhVideo.VhVideoImpl()
    }

    override suspend fun getVhVideoData(contentId: String): VideoData {
        return VhVideoData("", "")
    }

    override suspend fun setNextVideos(nextVideos: List<VhVideo>) {
        //noop
    }

    override suspend fun setPlayedVideos(playedVideos: List<VhVideo>) {
        //noop
    }

    override suspend fun getNearestEpisodes(serialContentId: String, season: Int,
                                            episodeNumber: Int, count: Int): List<VhVideo> {
        return emptyList()
    }

    override suspend fun updateEpisodesCount(serialContentId: String) {
        // noop
    }

    override suspend fun getContentDetails(contentId: String): ContentDetails? {
        return null
    }

    override suspend fun getContentMetadata(contentId: String): ContentMetadata? {
        return null
    }

    override suspend fun getStreamsMetadata(contentId: String): List<StreamMetadata> {
        return emptyList()
    }

    override fun getEpisodesCount(serialContentId: String, seasonNumber: Int): Int {
        return 0
    }

    override suspend fun getNextEpisodeContentId(serialContentId: String, season: Int, episode: Int): String? {
        return null
    }

    override suspend fun isActorsRecognitionEnabled(contentId: String): Boolean {
        return false
    }

    override suspend fun recognizeActors(contentId: String, atTimeMillis: Long): Array<ActorVideoRect> {
        return emptyArray()
    }

    override suspend fun getFilmography(actorId: Long): List<VhVideo> {
        return emptyList()
    }

    override suspend fun getRating(contentId: String): VideoRating? {
        return null
    }

    override suspend fun setRating(contentId: String, rating: VideoRating) {
        // noop
    }

    override suspend fun getWatchedStatus(contentId: String): VideoWatchedStatus? {
        return null
    }

    override suspend fun setWatchedStatus(contentId: String, watchedStatus: VideoWatchedStatus) {
        // noop
    }
}
