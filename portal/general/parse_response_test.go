package geohelper

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/morda-go/pkg/dto"
	"a.yandex-team.ru/portal/morda-go/tests/helpers"
)

// Check that regular and fast unmarshal got the same objects after marshaling to json
func TestParseResponseFast(t *testing.T) {
	response, err := helpers.THttpResponseParser("testdata/almost_prod.json")
	if err != nil {
		t.Fatal(err)
	}

	expected, err := ParseResponse(response)
	require.NoError(t, err)
	got, err := ParseResponseFast(response)
	require.NoError(t, err)

	expectedB, err := json.Marshal(expected)
	require.NoError(t, err)
	gotB, err := json.Marshal(got)
	require.NoError(t, err)

	require.Equal(t, expectedB, gotB)
}

func TestParseResponseFast1(t *testing.T) {
	type args struct {
		response *protoanswers.THttpResponse
	}
	tests := []struct {
		name    string
		args    args
		want    *dto.GeohelperResponse
		wantErr bool
	}{
		{
			name: "Empty json",
			args: args{
				response: &protoanswers.THttpResponse{Content: []byte("")},
			},
			wantErr: true,
		},
		{
			name: "Empty object",
			args: args{
				response: &protoanswers.THttpResponse{Content: []byte("{}")},
			},
			want: &dto.GeohelperResponse{Layout: []dto.GeohelperResponseLayoutItem{}, Blocks: []dto.GeohelperResponseBlock{}},
		},
		{
			name: "Array instead of object",
			args: args{
				response: &protoanswers.THttpResponse{Content: []byte("[]")},
			},
			want: &dto.GeohelperResponse{Layout: []dto.GeohelperResponseLayoutItem{}, Blocks: []dto.GeohelperResponseBlock{}},
		},
		{
			name: "String instead of object",
			args: args{
				response: &protoanswers.THttpResponse{Content: []byte("\"string\"")},
			},
			want: &dto.GeohelperResponse{Layout: []dto.GeohelperResponseLayoutItem{}, Blocks: []dto.GeohelperResponseBlock{}},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseResponseFast(tt.args.response)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}

func BenchmarkParseResponse(b *testing.B) {
	response, err := helpers.THttpResponseParser("testdata/almost_prod.json")
	if err != nil {
		b.Fatal(err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err = ParseResponse(response)
		if err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkParseResponseFast(b *testing.B) {
	response, err := helpers.THttpResponseParser("testdata/almost_prod.json")
	if err != nil {
		b.Fatal(err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err = ParseResponseFast(response)
		if err != nil {
			b.Fatal(err)
		}
	}
}

const multiCores = 8

func BenchmarkParseResponseMulti(b *testing.B) {
	response, err := helpers.THttpResponseParser("testdata/almost_prod.json")
	if err != nil {
		b.Fatal(err)
	}

	control := make(chan struct{}, multiCores)
	for k := 0; k < multiCores; k++ {
		go func() {
			for range control {
				_, _ = ParseResponse(response)
			}
		}()
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		control <- struct{}{}
	}
}

func BenchmarkParseResponseFastMulti(b *testing.B) {
	response, err := helpers.THttpResponseParser("testdata/almost_prod.json")
	if err != nil {
		b.Fatal(err)
	}

	control := make(chan struct{}, multiCores)
	for k := 0; k < multiCores; k++ {
		go func() {
			for range control {
				_, _ = ParseResponseFast(response)
			}
		}()
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		control <- struct{}{}
	}
}
