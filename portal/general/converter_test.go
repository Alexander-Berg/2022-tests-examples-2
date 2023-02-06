package postprocess

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"google.golang.org/protobuf/proto"

	"a.yandex-team.ru/maps/doc/proto/go/yandex/maps/proto/common2/geo_object"
	"a.yandex-team.ru/maps/doc/proto/go/yandex/maps/proto/common2/metadata"
	"a.yandex-team.ru/maps/doc/proto/go/yandex/maps/proto/common2/response"
	"a.yandex-team.ru/maps/doc/proto/go/yandex/maps/proto/search/address"
	"a.yandex-team.ru/maps/doc/proto/go/yandex/maps/proto/search/geocoder"
	"a.yandex-team.ru/maps/doc/proto/go/yandex/maps/proto/search/kind"
)

func createGeoObjectMetadata(address *address.Address) *metadata.Metadata {
	obj := metadata.Metadata{}
	proto.SetExtension(&obj, geocoder.E_GEO_OBJECT_METADATA, &geocoder.GeoObjectMetadata{
		Address: address,
	})
	return &obj
}

func Test_convertToMapAddrResponse(t *testing.T) {
	type testCase struct {
		name string
		arg  *response.Response

		want    *mapAddrResponse
		wantErr bool
	}

	cases := []testCase{
		{
			name:    "nil pointer",
			arg:     nil,
			want:    nil,
			wantErr: true,
		},
		{
			name: "nil reply",
			arg: &response.Response{
				Reply: nil,
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "no inner geoobjects",
			arg: &response.Response{
				Reply: &geo_object.GeoObject{
					GeoObject: nil,
				},
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "geoobject without metadata",
			arg: &response.Response{
				Reply: &geo_object.GeoObject{
					GeoObject: []*geo_object.GeoObject{
						{
							Metadata: nil,
						},
					},
				},
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "metadata without extension type needed",
			arg: &response.Response{
				Reply: &geo_object.GeoObject{
					GeoObject: []*geo_object.GeoObject{
						{
							Metadata: []*metadata.Metadata{
								{},
							},
						},
					},
				},
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "geo object metadata with address",
			arg: &response.Response{
				Reply: &geo_object.GeoObject{
					GeoObject: []*geo_object.GeoObject{
						{
							Metadata: []*metadata.Metadata{
								createGeoObjectMetadata(&address.Address{
									Component: []*address.Component{
										{
											Name: proto.String("Pushkina"),
											Kind: []kind.Kind{
												kind.Kind_STREET,
											},
										},
										{
											Name: proto.String("Kolotushkina"),
											Kind: []kind.Kind{
												kind.Kind_HOUSE,
											},
										},
									},
									FormattedAddress: proto.String("street of Pushkin, house of Kolotushkin"),
								}),
							},
						},
					},
				},
			},
			want: &mapAddrResponse{
				Components: []addressComponent{
					{
						Kind: "street",
						Name: "Pushkina",
					},
					{
						Kind: "house",
						Name: "Kolotushkina",
					},
				},
				FormattedAddress: "street of Pushkin, house of Kolotushkin",
				Show:             1,
				Type:             "MapAddr_formatted",
			},
			wantErr: false,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual, err := convertToMapAddrResponse(tt.arg)
			if tt.wantErr {
				assert.Error(t, err)
				assert.Nil(t, actual)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.want, actual)
			}
		})
	}
}
