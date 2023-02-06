package kannel

import (
	"math/rand"
	"net/http"
	"net/http/httptest"
	"time"

	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/utils"
)

func NewTestKannel(filename string) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.RequestURI {
		case KannelPingHandler:
			_, _ = w.Write(KannelPingResponse)
		case KannelStatusHandler:
			xml, _ := utils.FileContents(filename)
			_, _ = w.Write([]byte(xml))
		default:
			time.Sleep(time.Duration(rand.Intn(50)+50) * time.Millisecond)
			w.WriteHeader(http.StatusAccepted)
		}
	}))
}
