package uaasproxy

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/passport/shared/golibs/logger"
)

var handlerDivcardTests = []struct {
	name        string
	queryParams string
}{
	{
		"ru,light,default_rationale",
		"?lang=ru&color=light&card=default_rationale",
	},
	{
		"en,light,default_rationale",
		"?lang=en&color=light&card=default_rationale",
	},
	{
		"ru,dark,default_rationale",
		"?lang=ru&color=dark&card=default_rationale",
	},
	{
		"ru,light,default_blocked_rationale",
		"?lang=ru&color=light&card=default_blocked_rationale",
	},
	{
		"en,light,default_blocked_rationale",
		"?lang=en&color=light&card=default_blocked_rationale",
	},
	{
		"ru,dark,default_blocked_rationale",
		"?lang=ru&color=dark&card=default_blocked_rationale",
	},
}

func TestDivcardHandler(t *testing.T) {
	for _, tt := range handlerDivcardTests {
		t.Run(
			tt.name,
			func(t *testing.T) {
				req, err := http.NewRequest("GET", "/1/divcard"+tt.queryParams, nil)
				if err != nil {
					t.Fatal(err)
				}
				rec := httptest.NewRecorder()
				e := echo.New()
				c := e.NewContext(req, rec)

				app := &UaasProxy{
					unistat: InitUnistat(),
					logger:  logger.Log(),
				}
				app.InitPools()
				if assert.NoError(t, app.HandlerDivcard()(c)) {
					var actual map[string]interface{}
					assert.NotEqual(t, rec.Body.String(), "")
					err := json.Unmarshal(rec.Body.Bytes(), &actual)
					assert.NoError(t, err)
				}
			},
		)
	}
}
