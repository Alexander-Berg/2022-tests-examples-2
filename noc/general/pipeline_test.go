package pipeline

import (
	"testing"

	"github.com/stretchr/testify/assert"
	zzap "go.uber.org/zap"
	"go.uber.org/zap/zaptest/observer"

	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/metridat/internal/container"
)

func TestSpeed(t *testing.T) {
	zlcore, _ := observer.New(zzap.ErrorLevel)
	zl := zap.NewWithCore(zlcore)
	ppl := NewPipeline(zl)
	err := ppl.Add(".*", "speed", map[string]string{})
	assert.NoError(t, err)

	cont1 := container.NewContainerFull("test", container.Tags{"test": "norm1"}, container.Values{"testfield": container.UIntToAny(0)}, 1613302600_000)
	ppl.Cram(container.Containers{cont1})
	cont2 := container.NewContainerFull("test", container.Tags{"test": "norm1"}, container.Values{"testfield": container.UIntToAny(15_000)}, 1613302615_000)
	cont2Res := ppl.Cram(container.Containers{cont2})
	cont2Exp := container.NewContainerFull("test", container.Tags{"test": "norm1"}, container.Values{"testfield": container.UIntToAny(1_000)}, 1613302610_000)

	assert.Equal(t, cont2Res.Format(), (container.Containers{cont2Exp}).Format())

	cont3 := container.NewContainerFull("test", container.Tags{"test": "norm1"}, container.Values{"testfield": container.UIntToAny(30_000)}, 1613302630_000)
	cont3Res := ppl.Cram(container.Containers{cont3})
	cont3Exp1 := container.NewContainerFull("test", container.Tags{"test": "norm1"}, container.Values{"testfield": container.UIntToAny(1_000)}, 1613302620000)
	cont3Exp2 := container.NewContainerFull("test", container.Tags{"test": "norm1"}, container.Values{"testfield": container.UIntToAny(1_000)}, 1613302630000)
	assert.Equal(t, cont3Res.Format(), (container.Containers{cont3Exp1, cont3Exp2}).Format())
}
