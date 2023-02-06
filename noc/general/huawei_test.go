package device

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/gomocutor/pkg/expr"
)

func TestHuaweiErrors(t *testing.T) {
	errorCases := [][]byte{
		[]byte("             ^\r\nError: Unrecognized command found at '^' position.\r\n"),
		[]byte("\r\nError: You do not have permission to run the command or the command is incomplete.\r\n"),
	}
	exprTester(t, errorCases, huaweiErrorExpression)
}

func TestHuaweiPrompt(t *testing.T) {
	errorCases := [][]byte{
		[]byte("\r\n<ce8850-test>"),
	}
	exprTester(t, errorCases, huaweiPromptExpression)
}

func TestHuaweiQuestion(t *testing.T) {
	errorCases := [][]byte{
		[]byte("\r\nWarning: The current configuration will be written to the device. Continue? [Y/N]:"),
	}
	exprTester(t, errorCases, huaweiQuestionExpression)
}

func exprTester(t *testing.T, errorCases [][]byte, expression string) {
	errorExpr := expr.NewSimpleExpr(expression)
	for _, tc := range errorCases {
		t.Run("", func(t *testing.T) {
			res, ok := errorExpr.Match(tc)
			assert.True(t, ok, errorExpr.Repr())
			assert.NotNil(t, res)
		})
	}
}
