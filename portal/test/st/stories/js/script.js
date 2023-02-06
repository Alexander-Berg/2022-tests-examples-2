var initStoriesShowcase = function() {
    var storiesShowcase = document.querySelector('.st__showcase');

    if (!storiesShowcase) {
        return;
    }

    var wrapper = document.querySelector('.st__wrapper'),
        stories = wrapper.querySelectorAll('.st__story'),
        collapseAllStory = storiesShowcase.querySelector('.st__collapse_all'),
        openAllStory = storiesShowcase.querySelector('.st__open_all'),
        filters = storiesShowcase.querySelectorAll('.st__switcher'),
        phoneSelector = storiesShowcase.querySelector('.st__phone-select'),
        selectedCounter = storiesShowcase.querySelector('.st__selected-counter').querySelector('.st__switcher-counter'),
        counter_DB = (function () {
            var counter_DB = {};
            ['normal', 'type_content', 'type_maps_content', 'type_photo', 'type_mix', 'type_video', 'bad_video',
                'good_photo', 'bad_photo', 'skipped_all', 'skipped', 'skipped_geo', 'skipped_type', 'normal_bad_video'].forEach(function (item) {
                counter_DB[item] = 0;
            });
            return counter_DB;
        })(),
        order = 0;

    var init = function () {
        /**
         * Обработчик переключателя модели телефона
         */
        phoneSelector.addEventListener('change', function (event) {
            var model = event.target.value;
            selectPhoneMask(model);
        });
        /**
         * Обработчики для открытия\закрытия Story
         */
        wrapper.querySelectorAll('.st__slides-show').forEach(function (link) {
            link.addEventListener('click', function (event) {
                var story = event.target.parentElement,
                    openAction = story.classList.contains('st__story_collapsed');

                toggleStory(story, openAction);
            });
        });
        /**
         * Обработчик кнопки 'Свернуть все'
         */
        collapseAllStory.addEventListener('click', function () {
            stories.forEach(function (story) {
                toggleStory(story, false);
            });
        });
        /**
         * Обработчик кнопки 'Развернуть все'
         */
        openAllStory.addEventListener('click', function () {
            stories.forEach(function (story) {
                if (isVisible(story)) {
                    toggleStory(story, true);
                }
            });
        });
        /**
         * Парсим Stories, расставляем классы, составляем DB
         */
        stories.forEach(function (story) {
            // Классы принадлежности к сервису
            var id = story.id.match(/^[^:]+/)[0],
                hide = false;

            story.classList.add('st__story_type_' + id);

            if (id === 'content') {
                counter_DB.type_content += 1;
            } else if (id === 'maps_content') {
                counter_DB.type_maps_content += 1;
            }

            if (story.classList.contains('st__story_skipped')) {
                counter_DB.skipped += 1;
                hide = true;
            }

            if (story.classList.contains('st__story_skipped_geo')) {
                counter_DB.skipped_geo += 1;
                hide = true;
            }

            if (story.classList.contains('st__story_skipped_type')) {
                counter_DB.skipped_type += 1;
                hide = true;
            }

            if (hide) {
                counter_DB.skipped_all += 1;
            }

            var media_types = {
                video: false,
                bad_video: false,
                photo: false
            };

            // Классы фото и видео
            story.querySelectorAll('.st__slides').forEach(function (slide) {
                var type = slide.querySelector('.st__slide-type').innerText;
                if (type === 'video') {
                    media_types.video = true;
                    if (!slide.querySelector('video')) {
                        media_types.bad_video = true;
                    }
                } else if (type === 'photo') {
                    media_types.photo = true;
                }
            });

            if (media_types.video && media_types.photo) {
                counter_DB.type_mix += 1;
                story.classList.add('st__story_type_mix');
            } else if (media_types.video) {
                counter_DB.type_video += 1;
                story.classList.add('st__story_type_video');
            } else if (media_types.photo) {
                counter_DB.type_photo += 1;
                story.classList.add('st__story_type_photo');
            }

            if (media_types.bad_video) {
                counter_DB.bad_video += 1;
                story.classList.add('st__story_bad_video');
                if (!hide) {
                    counter_DB.normal_bad_video += 1;
                    story.classList.add('st__story_normal');
                }
                hide = true;
            }

            if (!hide) {
                counter_DB.normal += 1;
                story.classList.add('st__story_normal');
            }
        });
        /**
         *  Обработчики фильтров
         */
        filters.forEach(function (link) {
            // Раскладываем счетчики
            var counter = link.dataset,
                count_text = link.querySelector('.st__switcher-counter');

            if (counter['switch'] === 'service') {
                var service = counter.service;


                if (service === 'content') {
                    count_text.innerText = counter_DB.type_content;
                } else if (service === 'maps_content') {
                    count_text.innerText = counter_DB.type_maps_content;
                }

                count_text.classList.add('st__switcher-counter_active');
            }

            if (counter['switch'] === 'bad_video') {
                count_text.classList.add('st__switcher-counter_active');
                count_text.innerText = counter_DB.bad_video;
            }

            if (counter['switch'] === 'normal') {
                count_text.classList.add('st__switcher-counter_active');
                count_text.innerText = counter_DB.normal + ' + ' + counter_DB.normal_bad_video + ' неподдерживаемых';
            }

            if (counter['switch'] === 'skipped') {
                count_text.classList.add('st__switcher-counter_active');
                count_text.innerText = counter_DB.skipped;
            }

            if (counter['switch'] === 'skipped_geo') {
                count_text.classList.add('st__switcher-counter_active');
                count_text.innerText = counter_DB.skipped_geo;
            }

            if (counter['switch'] === 'skipped_type') {
                count_text.classList.add('st__switcher-counter_active');
                count_text.innerText = counter_DB.skipped_type;
            }

            if (counter['switch'] === 'type' && counter.type === 'video') {
                count_text.classList.add('st__switcher-counter_active');
                count_text.innerText = counter_DB.type_video;
            }

            if (counter['switch'] === 'type' && counter.type === 'photo') {
                count_text.classList.add('st__switcher-counter_active');
                count_text.innerText = counter_DB.type_photo;
            }

            link.addEventListener('click', function () {
                processFilterClick(link);
            });
        });
        /**
         *  Проставляем счетчик "Всего отфильтровано"
         */
        document.querySelector('.st__skipped-counter').innerText = counter_DB.skipped_all;
        /**
         *  Проставляем flex order
         */
        stories.forEach(function(story) {
            var storyStyle = story.style,
                hrStyle = story.nextElementSibling.style;
            if (!story.classList.contains('st__story_bad_video')) {
                storyStyle.order = hrStyle.order = order;
                order++;
            } else {
                storyStyle.order = hrStyle.order = stories.length - order;
            }
        });
        /**
         *  Проставляем счетчик "Выбрано"
         */
        setVisibleCounter(stories, selectedCounter);
    };
    /**
     * Обрабатывает клик по фильтру
     * @param {HTMLElement} link
     */
    var processFilterClick = function (link) {
        var attrs = link.dataset;

        if (attrs['switch'] === 'service') {
            var service = attrs.service;
            wrapper.classList.toggle('st__inactive_type_' + service);
            link.classList.toggle('st__switcher_active');
        } else if (attrs['switch'] === 'type') {
            var type = attrs.type;
            wrapper.classList.toggle('st__inactive_type_' + type);
            link.classList.toggle('st__switcher_active');
        } else if (attrs['switch'] === 'bad_video') {
            wrapper.classList.toggle('st__inactive_bad_video');
            wrapper.classList.toggle('st__force_bad_video');
            link.classList.toggle('st__switcher_active');
        } else if (attrs['switch'] === 'skipped') {
            wrapper.classList.toggle('st__inactive_skipped');
            link.classList.toggle('st__switcher_active');
            wrapper.classList.toggle('st__force_skipped');
        } else if (attrs['switch'] === 'skipped_geo') {
            wrapper.classList.toggle('st__inactive_skipped_geo');
            wrapper.classList.toggle('st__force_skipped_geo');
            link.classList.toggle('st__switcher_active');
        } else if (attrs['switch'] === 'skipped_type') {
            wrapper.classList.toggle('st__inactive_skipped_type');
            wrapper.classList.toggle('st__force_skipped_type');
            link.classList.toggle('st__switcher_active');
        } else if (attrs['switch'] === 'guidelines') {
            wrapper.classList.toggle('st__inactive_guidelines');
            link.classList.toggle('st__switcher_active');
        } else if (attrs['switch'] === 'normal') {
            wrapper.classList.toggle('st__inactive_normal');
            link.classList.toggle('st__switcher_active');
        }

        setVisibleCounter(stories, selectedCounter);

        // Закрыть отфильтрованные
        stories.forEach(function (story) {
            if (!isVisible(story) && story.classList.contains('st__story_open')) {
                toggleStory(story, false);
            }
        });
    };
    /**
     * Проверяет видимость элемента на странице (display: none)
     * @param {HTMLElement} elem
     */
    var isVisible = function (elem) {
        return window.getComputedStyle(elem, null).display !== 'none';
    };
    /**
     * Запускает видео в Story
     * @param {NodeList} Список Story
     * @param {HTMLElement} divElem Элемент счетчика
     */
    var setVisibleCounter = function (stories, divElem) {
        var selected_count = 0;
        stories.forEach(function (story) {
            if (isVisible(story)) {
                selected_count += 1;
            }
        });
        divElem.innerText = selected_count;
    };
    /**
     * Запускает видео в Story
     * @param {HTMLElement} story
     * @param {Boolean} status Проигрывать или останавливать видео
     */
    var playStoryVideo = function (story, status) {
        var videos = story.querySelectorAll('.stories__slide-video');

        if (videos.length) {
            if (status) {
                videos.forEach(function (player) {
                    var source = player.querySelector('.stories__slide-video-source');
                    source.src = source.dataset.src;
                    player.load();
                    player.play();
                });
            } else {
                videos.forEach(function (player) {
                    player.pause();
                });
            }
        }
    };
    /**
     * Скрывает или открывает Story
     * @param {HTMLElement} story
     * @param {Boolean} open
     */
    var toggleStory = function (story, open) {
        var doAfterDelay;

        if (open) {
            doAfterDelay = function (story) {
                playStoryVideo(story, true);
                story.classList.remove('st__story_collapsed');
                story.classList.add('st__story_open');
            };

            story.classList.remove('st__hide-helper');

            setTimeout(doAfterDelay, 100, story);
        } else {
            doAfterDelay = function (story) {
                story.classList.add('st__hide-helper');
            };
            playStoryVideo(story, false);
            story.classList.remove('st__story_open');
            story.classList.add('st__story_collapsed');
            setTimeout(doAfterDelay, 400, story);
        }
    };
    /**
     * Меняет класс обертки, устанавливающий маску телефона
     * @param {String} model
     */
    var selectPhoneMask = function (model) {
        var attr = wrapper.dataset.model;

        wrapper.classList.remove('st__phone_' + attr);
        wrapper.classList.add('st__phone_' + model);
        wrapper.dataset.model = model;
    };

    init();
};

document.addEventListener('DOMContentLoaded', function() {
    initStoriesShowcase();
});
