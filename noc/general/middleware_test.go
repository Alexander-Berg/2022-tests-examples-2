package api

import (
	"context"
	"net/http"
	"net/http/httptest"
	"reflect"
	"strings"
	"testing"

	"github.com/gofrs/uuid"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap"
	"go.uber.org/zap/zaptest/observer"

	"a.yandex-team.ru/library/go/core/log"
	yzap "a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/valid"
)

type testCase struct {
	name              string
	req               *http.Request
	expectedNextCalls int
	expectedCode      int
	expectedBody      string
}

func setupLogsCapture() (log.Logger, *observer.ObservedLogs) {
	core, logs := observer.New(zap.InfoLevel)
	logger := yzap.NewWithCore(core)
	return logger, logs
}

func Test_mwQueryObjectUUID(t *testing.T) {
	var tests = []testCase{
		{"empty request",
			httptest.NewRequest("GET", "/", nil),
			0, http.StatusBadRequest,
			`{"code":"400","message":"not fond object_uuid in query"}`},
		{"empty uuid",
			httptest.NewRequest("GET", "/?object_uuid=", nil),
			0, http.StatusBadRequest,
			`{"code":"400","message":"uuid: incorrect UUID length 0 in string \"\""}`},
		{"bad uuid", httptest.NewRequest("GET", "/?object_uuid=1234", nil),
			0, http.StatusBadRequest,
			`{"code":"400","message":"uuid: incorrect UUID length 4 in string \"1234\""}`},
		{"ok", httptest.NewRequest("GET", "/?object_uuid=64607f72-3e6a-438f-afc2-264c7f99de1e", nil),
			1, http.StatusOK,
			""},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			nextCalled := 0
			nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				nextCalled++
				val := r.Context().Value(vkObjectUUID)
				if val == nil {
					t.Error("ObjectUUID not present")
				}
				valUUID, ok := val.(*uuid.UUID)
				if !ok {
					t.Error("not UUID " + valUUID.String())
				}
				if valUUID.String() != "64607f72-3e6a-438f-afc2-264c7f99de1e" {
					t.Error("wrong ObjectUUID")
				}
			})
			mw := mwQueryObjectUUID()
			handlerToTest := mw(nextHandler)

			w := httptest.NewRecorder()
			handlerToTest.ServeHTTP(w, test.req)
			require.Equal(t, test.expectedNextCalls, nextCalled)
			require.Equal(t, test.expectedBody, w.Body.String())
			require.Equal(t, test.expectedCode, w.Code)
		})
	}
}

func Test_mwQueryIDInt32(t *testing.T) {
	var tests = []testCase{
		{"empty request",
			httptest.NewRequest("GET", "/", nil),
			0, http.StatusBadRequest,
			`{"code":"400","message":"not fond id in query"}`},
		{"empty id",
			httptest.NewRequest("GET", "/?id=", nil),
			0, http.StatusBadRequest,
			`{"code":"400","message":"strconv.ParseInt: parsing \"\": invalid syntax"}`},
		{"bad id", httptest.NewRequest("GET", "/?id=abc", nil),
			0, http.StatusBadRequest,
			`{"code":"400","message":"strconv.ParseInt: parsing \"abc\": invalid syntax"}`},
		{"ok", httptest.NewRequest("GET", "/?id=123", nil),
			1, http.StatusOK,
			""},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			nextCalled := 0
			nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				nextCalled++
				val := r.Context().Value(vkID).(int32)
				if val != 123 {
					t.Error("wrong ID")
				}
			})
			mw := mwQueryIDInt32()
			handlerToTest := mw(nextHandler)

			w := httptest.NewRecorder()
			handlerToTest.ServeHTTP(w, test.req)
			require.Equal(t, test.expectedNextCalls, nextCalled)
			require.Equal(t, test.expectedBody, w.Body.String())
			require.Equal(t, test.expectedCode, w.Code)
		})
	}
}

type testValidation struct {
	FieldUUID      string     `valid:"uuid4"`
	FieldNonEmpty1 string     `valid:"non_empty"`
	FieldNonEmpty2 *deepField `valid:"non_empty"`
	FieldRegexp    string     `valid:"regexp=^[a-z]\\d+$"`
	FieldRegexp2   string     `valid:"regexp=^\\d{4}-\\d{2}-\\d{2}$"`
}

type deepField struct {
	Field1 string
	Field2 string
}

type testCaseValidation struct {
	testCase
	val testValidation
}

func Test_mwValidationContext(t *testing.T) {
	var tests = []testCaseValidation{
		{
			testCase{"ok", httptest.NewRequest("GET", "/", nil),
				1, http.StatusOK, `"OK"`},
			testValidation{"64607f72-3e6a-438f-afc2-264c7f99de1e", "value",
				&deepField{"", ""}, "v42", "2222-33-44"}}, {
			testCase{"bad", httptest.NewRequest("GET", "/", nil),
				1, http.StatusBadRequest,
				`{"code":"400","message":"invalid string length; must not be empty; ` +
					`must not be empty; must match ^[a-z]\\d+$; must match ^\\d{4}-\\d{2}-\\d{2}$"}`},
			testValidation{"", "", nil, "", ""}},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			nextCalled := 0
			nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				nextCalled++
				val := r.Context().Value(vkValidationContext)
				if val == nil {
					t.Error("Validation context not present")
				}
				vctx, ok := val.(*valid.ValidationCtx)
				if !ok {
					t.Error("vctx not *valid.ValidationCtx: " + reflect.TypeOf(val).String())
				}
				if err := valid.Struct(vctx, test.val); err != nil {
					writeError(w, http.StatusBadRequest, err)
					return
				}
				writeOk(w, "OK")
			})

			mw := mwValidationContext()
			handlerToTest := mw(nextHandler)

			w := httptest.NewRecorder()
			handlerToTest.ServeHTTP(w, test.req)
			require.Equal(t, test.expectedNextCalls, nextCalled)
			require.Equal(t, test.expectedBody, w.Body.String())
			require.Equal(t, test.expectedCode, w.Code)
		})
	}
}

type testType struct {
	Field   string `json:"field"`
	Integer int    `json:"integer"`
}

func Test_mwDecodeJSONBody(t *testing.T) {
	var tests = []testCase{
		{"ok",
			httptest.NewRequest("POST", "/",
				strings.NewReader(`{"field":"f1","integer":123}`)),
			1, http.StatusOK, `"OK"`},
		{"bad",
			httptest.NewRequest("POST", "/",
				strings.NewReader(`{"field":"f1","integer":"123""}`)),
			0, http.StatusBadRequest,
			`{"code":"400","message":"can't decode json"}`},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			nextCalled := 0
			nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				nextCalled++
				val := r.Context().Value(vkObject)
				if val == nil {
					t.Error("object not present")
				}
				obj := val.(*testType)
				require.Equal(t, &testType{Field: "f1", Integer: 123}, obj)
				writeOk(w, "OK")
			})

			logger, _ := setupLogsCapture()
			mw := mwDecodeJSONBody(logger, reflect.TypeOf(testType{}))
			handlerToTest := mw(nextHandler)

			w := httptest.NewRecorder()
			handlerToTest.ServeHTTP(w, test.req)
			require.Equal(t, test.expectedNextCalls, nextCalled)
			require.Equal(t, test.expectedBody, w.Body.String())
			require.Equal(t, test.expectedCode, w.Code)
		})
	}
}

type testCaseValidObject struct {
	testCase
	valForValidation interface{}
}

func Test_mwValidObject(t *testing.T) {
	var tests = []testCaseValidObject{
		{testCase{"ok", httptest.NewRequest("POST", "/", nil),
			1, http.StatusOK, `"OK"`},
			nil},
		{testCase{"400 not struct", httptest.NewRequest("POST", "/", nil),
			0, http.StatusBadRequest,
			`{"code":"400","message":"param expected to be struct"}`},
			[]string{}},
		{testCase{"400 bad format", httptest.NewRequest("POST", "/", nil),
			0, http.StatusBadRequest,
			`{"code":"400","message":".FieldUUID: invalid string length.FieldNonEmpty1: must not be empty` +
				`.FieldNonEmpty2: must not be empty.FieldRegexp: must match ^[a-z]\\d+$` +
				`.FieldRegexp2: must match ^\\d{4}-\\d{2}-\\d{2}$"}`},
			testValidation{}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			nextCalled := 0
			nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				nextCalled++
				writeOk(w, "OK")
			})

			ctx := test.req.Context()
			test.req = test.req.WithContext(context.WithValue(ctx, vkObject, test.valForValidation))

			mwVC := mwValidationContext()
			mwVO := mwValidObject()
			handlerToTest := mwVC(mwVO(nextHandler))

			w := httptest.NewRecorder()
			handlerToTest.ServeHTTP(w, test.req)
			require.Equal(t, test.expectedNextCalls, nextCalled)
			require.Equal(t, test.expectedBody, w.Body.String())
			require.Equal(t, test.expectedCode, w.Code)
		})
	}
}
