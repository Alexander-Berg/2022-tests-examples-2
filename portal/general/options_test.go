package madm

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_optionsKeeper_parseToInterface(t *testing.T) {
	type fields struct {
		data interface{}
	}
	type args struct {
		i interface{}
		b []byte
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		want    interface{}
		wantErr bool
	}{
		{
			name: "Got struct with fields without tags",
			fields: fields{
				data: &structWithNoTag{},
			},
			args: args{
				i: &structWithNoTag{},
				b: []byte(`{"foo":{"value": "text"}}`),
			},
			want: &structWithNoTag{},
		},
		{
			name: "Got struct with all types with tags",
			fields: fields{
				data: &structWithSeveralTypes{},
			},
			args: args{
				i: &structWithSeveralTypes{},
				b: []byte(`{"ant":{"value": "insect"},"bear":{"value": "1"},"cat":{"value": "9"}}`),
			},
			want: &structWithSeveralTypes{
				Ant:  "insect",
				Bear: true,
				Cat:  9,
			},
		},
		{
			name: "Got struct with private attr",
			fields: fields{
				data: &structWithPrivateAttr{},
			},
			args: args{
				i: &structWithPrivateAttr{},
				b: []byte(`{"ant":{"value": "insect"},"bear":{"value": "1"},"cat":{"value": "9"}}`),
			},
			want: &structWithPrivateAttr{
				Ant:  "insect",
				bear: false,
			},
		},
		{
			name: "Got struct with embedding",
			fields: fields{
				data: &structWithEmbedding{},
			},
			args: args{
				i: &structWithEmbedding{},
				b: []byte(`{"ant":{"value": "insect"},"bear":{"value": "1"},"cat":{"value": "9"}}`),
			},
			want: &structWithEmbedding{
				Ant: "insect",
				structBearNCatEmbedded: structBearNCatEmbedded{
					Bear: true,
					structCatEmbedded: structCatEmbedded{
						Cat: 9,
					},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &optionsKeeper{
				data: tt.fields.data,
			}
			err := k.parseToInterface(tt.args.i, tt.args.b)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, tt.args.i)
			}
		})
	}
}

type structWithNoTag struct {
	Foo string
}

type structWithSeveralTypes struct {
	Ant  string `madm:"ant"`
	Bear bool   `madm:"bear"`
	Cat  int    `madm:"cat"`
}

type structWithPrivateAttr struct {
	Ant  string `madm:"ant"`
	bear bool   `madm:"bear"`
}

type structWithEmbedding struct {
	Ant string `madm:"ant"`

	structBearNCatEmbedded
}

type structBearNCatEmbedded struct {
	Bear bool `madm:"bear"`

	structCatEmbedded
}

type structCatEmbedded struct {
	Cat int `madm:"cat"`
}
