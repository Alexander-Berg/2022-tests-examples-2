# coding: utf-8


class TestConfig(object):
    export_qa_hosts = [
        'https://base.music.qa.yandex-team.ru'
    ]

    origs_test_endpoints = [
        'https://origs.mt.yandex-team.ru'
    ]

    export_qa_urls = [
        '/admin/account/index',
        '/admin/billing/music-account.action?uid=940081440',
        '/admin/billing/music-account?uid=940081440',
        '/admin/ads/',
        '/admin/alerts/',
        '/admin/arbitrary-image-list',
        '/admin/auroracharts/',
        '/admin/beta/',
        '/admin/changes-list',
        '/admin/chart/',
        '/admin/chart/',
        '/admin/chart/banned-tracks.action',
        '/admin/chart/view-regional-chart-config.action?region=WORLD',
        '/admin/charts/',
        '/admin/clip-list',
        '/admin/content-search',
        '/admin/contest/',
        '/admin/delivery-list',
        '/admin/digest/',
        '/admin/discography',
        '/admin/emails/',
        '/admin/explicit-artist-popular-albums-list',
        '/admin/feed/promo/',
        '/admin/feed/promo/edit-promotion.action?promoId=5d51b0f68e46e7341a62ae55',
        '/admin/feed/promo/edit-promotion.action?promoId=5d51478c45102c6af7337e58',
        '/admin/feed/promo/periods/',
        '/admin/genres/content/',
        '/admin/genres/similar/',
        '/admin/history/fake/',
        '/admin/ichwill/boost/',
        '/admin/ingest/',
        '/admin/interventions/artist-name-collisions-list',
        '/admin/junk/',
        '/admin/junk/labels.action',
        '/admin/label-list',
        '/admin/landing/editorial/',
        '/admin/landing/intents/',
        '/admin/landing/mixes/edit-mix?id=5ae44557cfd69fb3b9cc6d9f',
        '/admin/landing/nonmusic/blocks/',
        '/admin/landing/nonmusic/blocks/edit-podcasts-block?id=5cc8105db8d88e13c24716ca',
        '/admin/landing/nonmusic/catalogues/',
        '/admin/landing/nonmusic/categories/',
        '/admin/landing/nonmusic/editorials/',
        '/admin/landing/nonmusic/rubrics/',
        '/admin/landing/nonmusic/templates/',
        '/admin/major-list',
        '/admin/metagenre/order/index?name=ALL',
        '/admin/metatag/',
        '/admin/migration/',
        '/admin/muzsearch/music-search-requests.action',
        '/admin/play',
        '/admin/playlists/',
        '/admin/playlists/auto/',
        '/admin/playlists/auto/genre/view-playlist.action?genreId=16&type=RECENT&languageRestriction=ALL_LANGUAGES',
        '/admin/playlists/auto/genre/view-playlist.action?genreId=16&type=TOP&languageRestriction=ALL_LANGUAGES',
        '/admin/playlists/auto/genre/view-type.action?type=TOP',
        '/admin/playlists/auto/personal/view-type.action?type=PLAYLIST_OF_THE_DAY',
        '/admin/playlists/freshplaylists/',
        '/admin/playlists/hype/',
        '/admin/playlists/hype/',
        '/admin/playlists/search/',
        '/admin/playlists/search/index.action',
        '/admin/playlists/tags/',
        '/admin/playlists/tags/',
        '/admin/playlists/tags/edit-tag?id=5ae445f6cfd69fb3b9cc6dfd',
        '/admin/playlists/view-playlist-limits.action',
        '/admin/playlists/view-playlist.action?uid=103372440&kind=1175',
        '/admin/playlists/view-playlist.action?uid=103372440&kind=1829',
        '/admin/playlists/view-playlist.action?uid=460140864&kind=1000',
        '/admin/playlists/view-top.action',
        '/admin/preroll/',
        '/admin/preroll/',
        '/admin/promocodes',
        '/admin/promocodes/campaignpromos/',
        '/admin/radiostream/',
        '/admin/reports/finance/',
        '/admin/samples/',
        '/admin/search-auto-playlists',
        '/admin/search/trends/',
        # '/admin/shots/', # Disabled. Reason: Mongo timeouts. Huge collection music_shots.shots, size: 29264558
        '/admin/similarities/',
        '/admin/statistics/',
        '/admin/statistics/access/',
        '/admin/subeditors/',
        '/admin/subeditors/changes/',
        '/admin/support/user-personal-playlist?uidOrLogin=12591276&type=PLAYLIST_OF_THE_DAY',
        '/admin/teasers/edit-teaser?id=5d35d6b792a60f37fe533524',
        '/admin/teasers/edit-teaser?id=5d51b4b65d0b01382a4e55b5',
        '/admin/ugc/',
        '/admin/users/verified/',
        '/admin/versions/',
        '/admin/videos/banned/',
        '/admin/view-album?albumId=147821',
        '/admin/view-album?albumId=297720',
        '/admin/view-album?albumId=2298519',
        '/admin/view-album?albumId=6270545',
        '/admin/view-album?albumId=8096326',
        '/admin/view-album?albumId=8315669',
        '/admin/view-label?labelId=1746829',
        '/admin/view-meta-genre?name=ALL',
        '/admin/view-track?trackId=3684312',
        '/admin/view-track?trackId=54658350',
        '/z/rotor/',
        '/z/rotor/',
    ]

    origs_test_urls = [
        '/incoming/podcast/',
        '/incoming/file/',
    ]


TEST_CONFIG = TestConfig()
