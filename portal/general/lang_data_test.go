package weather

import (
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestLangDataFromJSON(t *testing.T) {
	type testCase struct {
		name string
		json string
		data langData
	}

	testcases := []testCase{
		{
			name: "empty json",
			json: "{}",
			data: langData{map[string]wordTranslations{}},
		},
		{
			name: "one word",
			json: `{
					"cloudy" : {
						  "be" : "воблачна з праясненнямі",
						  "en" : "partly cloudy",
						  "fr" : "belles éclaircies",
						  "it" : "poco nuvoloso",
						  "kk" : "ауыспалы бұлтты",
						  "pt" : "parcialmente nublado",
						  "ru" : "облачно с прояснениями",
						  "tr" : "parçalı bulutlu",
						  "tt" : "аязучан болытлы",
						  "uk" : "хмарно із проясненнями ",
						  "uz" : "bulutli, vaqti-vaqti bilan ochiq"
					   }
					}
				`,
			data: langData{
				map[string]wordTranslations{
					"cloudy": {
						"be": "воблачна з праясненнямі",
						"en": "partly cloudy",
						"fr": "belles éclaircies",
						"it": "poco nuvoloso",
						"kk": "ауыспалы бұлтты",
						"pt": "parcialmente nublado",
						"ru": "облачно с прояснениями",
						"tr": "parçalı bulutlu",
						"tt": "аязучан болытлы",
						"uk": "хмарно із проясненнями ",
						"uz": "bulutli, vaqti-vaqti bilan ochiq",
					},
				}},
		},
		{
			name: "many words",
			json: `{
				"P": {"ru": "П", "en": "P"},
				"L": {"ru": "Л", "en": "L"}}`,
			data: langData{map[string]wordTranslations{
				"P": {"ru": "П", "en": "P"},
				"L": {"ru": "Л", "en": "L"},
			}},
		},
	}

	for _, tc := range testcases {
		t.Run(tc.name, func(t *testing.T) {
			data, err := newLangDataFromJSON([]byte(tc.json))
			require.NoError(t, err)
			assert.Equal(t, *data, tc.data)
		})
	}
}

func TestUpdate(t *testing.T) {
	type cacheRequest struct {
		word string
		lang string
		tran string
		alt  string
	}

	cache := &langDataCache{&langData{
		map[string]wordTranslations{
			"A": {"1": "x", "2": "xx"},
			"B": {"1": "y", "2": "yy"},
		}}, &sync.RWMutex{},
	}

	requests := []cacheRequest{
		{"A", "1", "x", "y"},
		{"B", "1", "y", "x"},
		{"B", "2", "yy", "xx"},
	}

	ddosCache := func(cache *langDataCache, req cacheRequest, dur time.Duration, wg *sync.WaitGroup) {
		reqs := make(chan cacheRequest, 1)
		defer wg.Done()

		go func() {
			timeout := time.After(dur)
			for {
				select {
				case <-timeout:
					close(reqs)
					return
				default:
					reqs <- req
				}
			}
		}()

		i := 0
		for r := range reqs {
			actual := cache.GetData().Translate(r.word, r.lang)
			assert.True(t, actual == r.tran || actual == r.alt)
			i++
		}
		if i < 10 {
			t.FailNow()
		}
	}

	newData := `{
					"A": {
						"1": "y",
						"2": "yy"
					},
					"B": {
						"1": "x",
						"2": "xx"
					}
	}`

	t.Run("concurrent cache consistency", func(t *testing.T) {
		var wg sync.WaitGroup
		for _, req := range requests {
			wg.Add(1)
			go ddosCache(cache, req, time.Second, &wg)
		}
		time.Sleep(400 * time.Millisecond)
		err := cache.Update([]byte(newData))
		require.NoError(t, err)
		wg.Wait()
	})
}
