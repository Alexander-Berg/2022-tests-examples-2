package swaggermur

import (
	"bytes"
	"encoding/json"
	"os"
	"testing"

	"github.com/go-openapi/spec"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/cmdb/pkg/auth"
	"a.yandex-team.ru/noc/cmdb/pkg/configuration"
	"a.yandex-team.ru/noc/cmdb/pkg/mur"
	"a.yandex-team.ru/noc/cmdb/pkg/murspec"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestMurSpec(t *testing.T) {

	lg, _ := zap.New(zap.ConsoleConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)

	r, err := configuration.NewRouter{
		DB:                    nil,
		Logger:                logger,
		IDMCheckServiceTicket: &auth.DoNotCheckServiceTicket{},
		CheckServiceTicket:    &auth.DoNotCheckServiceTicket{},
		CheckUserTicket:       &auth.TryCheckUserTicket{},
		NewSession:            mur.NewSession{Logger: logger, DebugHeader: configuration.XDebugCMDB},
	}.NewRouter()
	require.NoError(t, err)

	serviceSpec, err := murspec.Generate(r, murspec.Head{
		Swagger: "2.0",
		Info: &spec.Info{InfoProps: spec.InfoProps{
			Title: "CMDB",
		}},
	})
	require.NoError(t, err)

	expected, err := os.ReadFile("swagger.json")
	require.NoError(t, err)

	buffer := bytes.NewBuffer(nil)
	e := json.NewEncoder(buffer)
	e.SetIndent("", "    ")
	err = e.Encode(serviceSpec)
	require.NoError(t, err)

	_ = os.WriteFile("swagger.json", buffer.Bytes(), 0755)

	require.Equal(t, string(expected), buffer.String())
}
