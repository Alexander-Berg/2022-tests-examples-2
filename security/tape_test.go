package tape_test

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/stretchr/testify/require"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/timestamppb"

	"a.yandex-team.ru/library/go/test/requirepb"
	"a.yandex-team.ru/security/libs/go/boombox/httpmodel"
	"a.yandex-team.ru/security/libs/go/boombox/tape"
)

func TestTape(t *testing.T) {
	cases := []struct {
		bucket string
		key    string
		item   proto.Message
	}{
		{
			bucket: "first",
			key:    "time1",
			item: &timestamppb.Timestamp{
				Seconds: 544665600,
				Nanos:   0,
			},
		},
		{
			bucket: "first",
			key:    "time2",
			item: &timestamppb.Timestamp{
				Seconds: 544665699,
				Nanos:   0,
			},
		},
		{
			bucket: "second",
			key:    "rsp1",
			item: &httpmodel.Response{
				StatusCode: 200,
				Body:       []byte("body"),
				UpdatedAt: &timestamppb.Timestamp{
					Seconds: 544665611,
					Nanos:   0,
				},
				Headers: []*httpmodel.Header{
					{
						Name: "X-Test",
						Values: []string{
							"Val1",
							"Val2",
						},
					},
				},
			},
		},
		{
			bucket: "second",
			key:    "rsp2",
			item: &httpmodel.Response{
				StatusCode: 404,
				UpdatedAt: &timestamppb.Timestamp{
					Seconds: 544665612,
					Nanos:   0,
				},
			},
		},
	}

	tapePath := tapeName(t)

	t.Run("rw", func(t *testing.T) {
		tt, err := tape.NewTape(tapePath)
		require.NoError(t, err)

		for _, tc := range cases {
			t.Run(tc.key, func(t *testing.T) {
				err := tt.Save(tc.bucket, tc.key, tc.item)
				require.NoError(t, err)

				actual := reflect.New(reflect.TypeOf(tc.item).Elem()).Interface().(proto.Message)
				err = tt.Get(tc.bucket, tc.key, actual)
				require.NoError(t, err)
				requirepb.Equal(t, tc.item, actual)
			})
		}

		err = tt.Close()
		require.NoError(t, err)
	})

	t.Run("ro", func(t *testing.T) {
		tt, err := tape.NewTape(tapePath, tape.WithReadOnly())
		require.NoError(t, err)

		for _, tc := range cases {
			t.Run(tc.key, func(t *testing.T) {
				actual := reflect.New(reflect.TypeOf(tc.item).Elem()).Interface().(proto.Message)
				err = tt.Get(tc.bucket, tc.key, actual)
				require.NoError(t, err)
				requirepb.Equal(t, tc.item, actual)
			})
		}

		err = tt.Close()
		require.NoError(t, err)
	})
}

func TestTape_http(t *testing.T) {
	cases := []struct {
		bucket string
		key    string
		item   *httpmodel.Response
	}{
		{
			bucket: "responses",
			key:    "rsp1",
			item: &httpmodel.Response{
				StatusCode: 200,
				Body:       []byte("body"),
				UpdatedAt: &timestamppb.Timestamp{
					Seconds: 544665611,
					Nanos:   0,
				},
				Headers: []*httpmodel.Header{
					{
						Name: "X-Test",
						Values: []string{
							"Val1",
							"Val2",
						},
					},
				},
			},
		},
		{
			bucket: "second",
			key:    "rsp2",
			item: &httpmodel.Response{
				StatusCode: 404,
				UpdatedAt: &timestamppb.Timestamp{
					Seconds: 544665612,
					Nanos:   0,
				},
			},
		},
	}

	tapePath := tapeName(t)

	t.Run("rw", func(t *testing.T) {
		tt, err := tape.NewTape(tapePath)
		require.NoError(t, err)

		for _, tc := range cases {
			t.Run(tc.key, func(t *testing.T) {
				err := tt.Save(tc.bucket, tc.key, tc.item)
				require.NoError(t, err)

				actual := new(httpmodel.Response)
				err = tt.Get(tc.bucket, tc.key, actual)
				require.NoError(t, err)
				requirepb.Equal(t, tc.item, actual)
			})
		}

		err = tt.Close()
		require.NoError(t, err)
	})

	t.Run("ro", func(t *testing.T) {
		tt, err := tape.NewTape(tapePath, tape.WithReadOnly())
		require.NoError(t, err)

		for _, tc := range cases {
			t.Run(tc.key, func(t *testing.T) {
				actual := new(httpmodel.Response)
				err = tt.Get(tc.bucket, tc.key, actual)
				require.NoError(t, err)
				requirepb.Equal(t, tc.item, actual)
			})
		}

		err = tt.Close()
		require.NoError(t, err)
	})
}

func tapeName(t *testing.T) string {
	return fmt.Sprintf("%s.bolt", t.Name())
}
