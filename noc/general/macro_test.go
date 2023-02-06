package macro

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/resource"
)

func TestNames_TraverseMacroListEmpty(t *testing.T) {
	data := ""

	macrosList, err := ParseMacroNames(strings.NewReader(data))
	require.NoError(t, err)
	require.Nil(t, macrosList)
}

func TestNames_TraverseMacroListSimple(t *testing.T) {
	data := `_YANDEXNETS_:	 dnl
n1.yandex-team.ru or dnl
n2.yandex-team.ru dnl`

	macrosList, err := ParseMacroNames(strings.NewReader(data))
	require.NoError(t, err)
	require.NotNil(t, macrosList)

	assert.Equal(t, []string{"_YANDEXNETS_"}, macrosList)
}

func TestNames_TraverseMacroListIgnoreInvalid(t *testing.T) {
	data := `YANDEXNETS_:	 dnl
n1.yandex-team.ru or dnl
n2.yandex-team.ru dnl`

	macrosList, err := ParseMacroNames(strings.NewReader(data))
	require.NoError(t, err)
	require.Nil(t, macrosList)
}

func TestNames_TraverseMacroListTwo(t *testing.T) {
	data := `
_1CAPPSRV_:	 dnl
keniya-n1.yandex-team.ru or dnl
keniya-n2.yandex-team.ru dnl

_1CBACKUPSRV_:	 dnl
1cbackup-n1.yandex-team.ru or dnl
1cbackup-n2.yandex-team.ru dnl

_1CDEVSRV_:	 dnl
ghoom.yandex-team.ru dnl
`

	macrosList, err := ParseMacroNames(strings.NewReader(data))
	require.NoError(t, err)
	require.NotNil(t, macrosList)

	assert.Equal(t, []string{"_1CAPPSRV_", "_1CBACKUPSRV_", "_1CDEVSRV_"}, macrosList)
}

func TestNames_TraverseMacro(t *testing.T) {
	rd := strings.NewReader(string(resource.MustGet("macros-inc.txt")))

	macrosList, err := ParseMacroNames(rd)
	require.NoError(t, err)
	require.NotNil(t, macrosList)

	assert.Equal(t, 44148, len(macrosList))
}

func Test_TraverseMacroListSimple(t *testing.T) {
	data := `_YANDEXNETS_:	 dnl
n1.yandex-team.ru or dnl
n2.yandex-team.ru dnl`

	macrosList, err := parseMacros(strings.NewReader(data))
	require.NoError(t, err)
	require.NotNil(t, macrosList)

	assert.Equal(t, map[string][]string{
		"_YANDEXNETS_": {"n1.yandex-team.ru", "n2.yandex-team.ru"},
	}, macrosList)
}

func Test_TraverseMacroListTwo(t *testing.T) {
	data := `
_1CAPPSRV_:	 dnl
keniya-n1.yandex-team.ru or dnl
keniya-n2.yandex-team.ru dnl

_1CBACKUPSRV_:	 dnl
1cbackup-n1.yandex-team.ru or dnl
1cbackup-n2.yandex-team.ru dnl

_1CDEVSRV_:	 dnl
ghoom.yandex-team.ru dnl
`

	macrosList, err := parseMacros(strings.NewReader(data))
	require.NoError(t, err)
	require.NotNil(t, macrosList)

	assert.Equal(t, map[string][]string{
		"_1CAPPSRV_":    {"keniya-n1.yandex-team.ru", "keniya-n2.yandex-team.ru"},
		"_1CBACKUPSRV_": {"1cbackup-n1.yandex-team.ru", "1cbackup-n2.yandex-team.ru"},
		"_1CDEVSRV_":    {"ghoom.yandex-team.ru"},
	}, macrosList)
}

func Test_TraverseMacroListIgnoreTrash(t *testing.T) {
	data := `BEGIN_AUTO_SECTION:
END_AUTO_SECTION:
TRYPO_RANGE_SUPPORT:
TRYPO_SUPPORT:
_YANDEXNETS_:	 dnl
n1.yandex-team.ru or dnl
n2.yandex-team.ru dnl
`

	macrosList, err := parseMacros(strings.NewReader(data))
	require.NoError(t, err)
	require.NotNil(t, macrosList)

	assert.Equal(t, map[string][]string{
		"_YANDEXNETS_": {"n1.yandex-team.ru", "n2.yandex-team.ru"},
	}, macrosList)
}

func Test_TraverseMacroListIgnoreBuiltins(t *testing.T) {
	data := `BEGIN_AUTO_SECTION:
END_AUTO_SECTION:
TRYPO_RANGE_SUPPORT:
TRYPO_SUPPORT:
_YANDEXNETS_:	 dnl
n1.yandex-team.ru or dnl
n2.yandex-team.ru dnl
__RASPRZDPROXY_TUN64_NETS_:     240.0.0.0/32
__file__:       <__file__>
__gnu__:
__line__:       <__line__>
__program__:    <__program__>
__unix__:
_fmt_pid_v6:    dnl
builtin:        <builtin>
changecom:      <changecom>
changequote:    <changequote>
debugfile:      <debugfile>
debugmode:      <debugmode>
decr:   <decr>
define: <define>
defn:   <defn>
divert: <divert>
divnum: <divnum>
dnl:    <dnl>
dumpdef:        <dumpdef>
errprint:       <errprint>
esyscmd:        <esyscmd>
eval:   <eval>
fmt_bb_pid:     $1@2a02:6b8:c00::/40
fmt_fb_pid:     $1@2a02:6b8:fc00::/40
format: <format>
ifdef:  <ifdef>
ifelse: <ifelse>
include:        <include>
incr:   <incr>
index:  <index>
indir:  <indir>
len:    <len>
m4exit: <m4exit>
m4wrap: <m4wrap>
maketemp:       <maketemp>
patsubst:       <patsubst>
popdef: <popdef>
pushdef:        <pushdef>
regexp: <regexp>
shift:  <shift>
sinclude:       <sinclude>
substr: <substr>
syscmd: <syscmd>
sysval: <sysval>
traceoff:       <traceoff>
traceon:        <traceon>
translit:       <translit>
undefine:       <undefine>
undivert:       <undivert>
`

	macrosList, err := parseMacros(strings.NewReader(data))
	require.NoError(t, err)
	require.NotNil(t, macrosList)

	assert.Equal(t, map[string][]string{
		"_YANDEXNETS_":               {"n1.yandex-team.ru", "n2.yandex-team.ru"},
		"__RASPRZDPROXY_TUN64_NETS_": {"240.0.0.0/32"},
	}, macrosList)
}
