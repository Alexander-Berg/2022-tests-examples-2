package yasms

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestProcessor_GetYaSmsTemplateTokens(t *testing.T) {
	fields, err := GetYaSmsTemplateTokens("Test syntax {{field}} new {{code111}}")
	require.NoError(t, err)
	require.Equal(t, []string{"field", "code111"}, fields)

	fields, err = GetYaSmsTemplateTokens("Test syntax")
	require.NoError(t, err)
	require.Equal(t, []string{}, fields)

	fields, err = GetYaSmsTemplateTokens("{{code}}")
	require.NoError(t, err)
	require.Equal(t, []string{"code"}, fields)

	fields, err = GetYaSmsTemplateTokens("My {{code}} and {some}")
	require.NoError(t, err)
	require.Equal(t, []string{"code"}, fields)

	fields, err = GetYaSmsTemplateTokens("My {{code}} and {some}")
	require.NoError(t, err)
	require.Equal(t, []string{"code"}, fields)

	fields, err = GetYaSmsTemplateTokens("My { {code}} and {{some}}")
	require.NoError(t, err)
	require.Equal(t, []string{"some"}, fields)

	_, err = GetYaSmsTemplateTokens("My {{code}} and {{some}} {{")
	require.Error(t, err)

	_, err = GetYaSmsTemplateTokens("My {{code }} and {{some}} {{")
	require.Error(t, err)

	_, err = GetYaSmsTemplateTokens("My {{code and {{some}}")
	require.Error(t, err)
}
