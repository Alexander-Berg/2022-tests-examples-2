package s3

import (
	"bytes"
	"context"
	"fmt"
	"io/ioutil"
	"math/rand"
	"sort"
	"strconv"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	awsRequest "github.com/aws/aws-sdk-go/aws/request"
	awsS3 "github.com/aws/aws-sdk-go/service/s3"
	"github.com/pierrec/lz4"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/osquery/osquery-sender/batcher"
	"a.yandex-team.ru/security/osquery/osquery-sender/metrics"
	"a.yandex-team.ru/security/osquery/osquery-sender/parser"
)

var testBucket = "testBucket"

type mockUpload struct {
	key      string
	metadata map[string]*string
	parts    []mockPart
}

type mockPart struct {
	partNumber int64
	etag       string
	data       []byte
}

type s3ClientMock struct {
	t *testing.T

	mu sync.Mutex

	// key -> contents
	objects map[string][]byte
	// key -> metadata
	metadata map[string]map[string]*string

	// upload id -> upload
	uploads map[string]*mockUpload

	nextUploadID int64
}

func (s *s3ClientMock) CopyObjectWithContext(ctx context.Context, input *awsS3.CopyObjectInput, _ ...awsRequest.Option) (*awsS3.CopyObjectOutput, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	parts := strings.SplitN(*input.CopySource, "/", 1)
	bucket, srcKey := parts[0], parts[1]
	require.Equal(s.t, testBucket, bucket)
	require.Equal(s.t, testBucket, *input.Bucket)
	data, ok := s.objects[srcKey]
	require.True(s.t, ok)
	metadata, ok := s.metadata[srcKey]
	require.True(s.t, ok)
	var newData []byte
	newData = append(newData, data...)
	newMetadata := make(map[string]*string)
	for k, v := range metadata {
		newMetadata[k] = v
	}
	s.objects[*input.Key] = newData
	s.metadata[*input.Key] = newMetadata
	return &awsS3.CopyObjectOutput{}, nil
}

func (s *s3ClientMock) AbortMultipartUploadWithContext(context.Context, *awsS3.AbortMultipartUploadInput, ...awsRequest.Option) (*awsS3.AbortMultipartUploadOutput, error) {
	s.t.Error("aborted upload")
	return nil, nil
}

func (s *s3ClientMock) CompleteMultipartUploadWithContext(_ context.Context, input *awsS3.CompleteMultipartUploadInput, _ ...awsRequest.Option) (*awsS3.CompleteMultipartUploadOutput, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	upload, ok := s.uploads[*input.UploadId]
	require.True(s.t, ok)
	require.Equal(s.t, testBucket, *input.Bucket)
	require.Equal(s.t, upload.key, *input.Key)

	sort.Slice(input.MultipartUpload.Parts, func(i, j int) bool {
		return *input.MultipartUpload.Parts[i].PartNumber < *input.MultipartUpload.Parts[j].PartNumber
	})
	sort.Slice(upload.parts, func(i, j int) bool {
		return upload.parts[i].partNumber < upload.parts[j].partNumber
	})
	require.Equal(s.t, len(upload.parts), len(input.MultipartUpload.Parts))
	for i := 0; i < len(upload.parts); i++ {
		require.Equal(s.t, upload.parts[i].partNumber, *input.MultipartUpload.Parts[i].PartNumber)
		require.Equal(s.t, int64(i+1), *input.MultipartUpload.Parts[i].PartNumber)
		require.Equal(s.t, upload.parts[i].etag, *input.MultipartUpload.Parts[i].ETag)
	}

	var allData bytes.Buffer
	// Parts are already sorted by the partNumber.
	for _, part := range upload.parts {
		allData.Write(part.data)
	}

	delete(s.uploads, *input.UploadId)
	s.objects[upload.key] = allData.Bytes()
	s.metadata[upload.key] = upload.metadata

	return &awsS3.CompleteMultipartUploadOutput{
		Bucket: &testBucket,
		Key:    &upload.key,
	}, nil
}

func (s *s3ClientMock) CreateMultipartUploadWithContext(_ context.Context, input *awsS3.CreateMultipartUploadInput, _ ...awsRequest.Option) (*awsS3.CreateMultipartUploadOutput, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	require.Equal(s.t, testBucket, *input.Bucket)

	uploadID := fmt.Sprintf("upload-%d", s.nextUploadID)
	s.nextUploadID++
	s.uploads[uploadID] = &mockUpload{
		key:      *input.Key,
		metadata: input.Metadata,
	}

	return &awsS3.CreateMultipartUploadOutput{
		Bucket:   input.Bucket,
		Key:      input.Key,
		UploadId: &uploadID,
	}, nil
}

func (s *s3ClientMock) DeleteObjectsWithContext(_ context.Context, input *awsS3.DeleteObjectsInput, _ ...awsRequest.Option) (*awsS3.DeleteObjectsOutput, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	require.Equal(s.t, testBucket, *input.Bucket)

	var result []*awsS3.DeletedObject
	for _, d := range input.Delete.Objects {
		_, ok := s.objects[*d.Key]
		require.True(s.t, ok)
		delete(s.objects, *d.Key)
		result = append(result, &awsS3.DeletedObject{
			Key: d.Key,
		})
	}

	return &awsS3.DeleteObjectsOutput{
		Deleted: result,
	}, nil
}

type mockReadCloser struct {
	inner *bytes.Reader
}

func (m *mockReadCloser) Read(p []byte) (n int, err error) {
	return m.inner.Read(p)
}

func (m *mockReadCloser) Close() error {
	return nil
}

func (s *s3ClientMock) GetObjectWithContext(_ context.Context, input *awsS3.GetObjectInput, _ ...awsRequest.Option) (*awsS3.GetObjectOutput, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	require.Equal(s.t, testBucket, *input.Bucket)

	data, ok := s.objects[*input.Key]
	if !ok {
		return nil, fmt.Errorf("no %s key found", *input.Key)
	}

	chunk := data
	if input.Range != nil {
		var from int
		var to int
		n, err := fmt.Sscanf(*input.Range, "bytes=%d-%d", &from, &to)
		if err != nil || n != 2 {
			return nil, fmt.Errorf("range is in improper format: %s", *input.Range)
		}
		if to >= len(data) {
			to = len(data) - 1
		}
		chunk = data[from : to+1]
	}

	return &awsS3.GetObjectOutput{
		Body: &mockReadCloser{
			inner: bytes.NewReader(chunk),
		},
		ContentLength: aws.Int64(int64(len(chunk))),
	}, nil
}

func (s *s3ClientMock) HeadObjectWithContext(_ context.Context, input *awsS3.HeadObjectInput, _ ...awsRequest.Option) (*awsS3.HeadObjectOutput, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	require.Equal(s.t, testBucket, *input.Bucket)

	metadata, ok := s.metadata[*input.Key]
	if !ok {
		return nil, fmt.Errorf("no %s key found", *input.Key)
	}

	return &awsS3.HeadObjectOutput{
		Metadata: metadata,
	}, nil
}

func (s *s3ClientMock) ListObjectsV2WithContext(_ context.Context, input *awsS3.ListObjectsV2Input, _ ...awsRequest.Option) (*awsS3.ListObjectsV2Output, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	require.Equal(s.t, testBucket, *input.Bucket)

	var contents []*awsS3.Object
	for key, data := range s.objects {
		key := key
		contents = append(contents, &awsS3.Object{
			Key:  &key,
			Size: aws.Int64(int64(len(data))),
		})
	}

	// Ignore all filters and continuation token.
	return &awsS3.ListObjectsV2Output{
		Contents:    contents,
		IsTruncated: aws.Bool(false),
		KeyCount:    aws.Int64(int64(len(contents))),
	}, nil
}

func (s *s3ClientMock) PutObjectWithContext(_ context.Context, input *awsS3.PutObjectInput, _ ...awsRequest.Option) (*awsS3.PutObjectOutput, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	data, err := ioutil.ReadAll(input.Body)
	require.NoError(s.t, err)
	s.objects[*input.Key] = data
	s.metadata[*input.Key] = input.Metadata

	return &awsS3.PutObjectOutput{}, nil
}

func (s *s3ClientMock) UploadPartWithContext(_ context.Context, input *awsS3.UploadPartInput, _ ...awsRequest.Option) (*awsS3.UploadPartOutput, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	upload, ok := s.uploads[*input.UploadId]
	require.True(s.t, ok)
	require.Equal(s.t, testBucket, *input.Bucket)
	require.Equal(s.t, upload.key, *input.Key)

	etag := strconv.Itoa(rand.Int())
	data, err := ioutil.ReadAll(input.Body)
	require.NoError(s.t, err)
	upload.parts = append(upload.parts, mockPart{
		partNumber: *input.PartNumber,
		etag:       etag,
		data:       data,
	})

	return &awsS3.UploadPartOutput{
		ETag: &etag,
	}, nil
}

var _ S3Client = (*s3ClientMock)(nil)

func TestS3(t *testing.T) {
	s3Client := &s3ClientMock{
		t:        t,
		objects:  map[string][]byte{},
		metadata: map[string]map[string]*string{},
		uploads:  map[string]*mockUpload{},
	}

	manager := NewS3Manager(s3Client, &S3ManagerConfig{
		EnableDebug:        true,
		NumRetries:         10,
		NumDownloadWorkers: 4,
		NumUploadWorkers:   4,
		NumGetInfoWorkers:  4,
		MinUploadPartSize:  1000,
	})

	merger := &s3Merger{
		enableDebug:           true,
		bucket:                testBucket,
		manager:               manager,
		mergedAlg:             CompressionLz4,
		loc:                   time.UTC,
		deleteMergedAfterDays: 1,
		mergerLoad:            metrics.NewLoadReporter(time.Hour * 24),
	}

	// This is very hacked-up: we fill only the required fields in S3Sender.
	sender := &S3Sender{
		enableDebug: true,
		manager:     manager,
		bucket:      testBucket,
		alg:         CompressionSnappy,
		loc:         time.UTC,
		merger:      merger,
	}
	eventBatcher := batcher.New(nil, nil, true, nil)
	workers := batcher.NewWorkers(eventBatcher, batcher.WorkersConfig{MaxWorkers: 0}, sender, "")
	sender.workers = workers

	sender.Start()

	events1 := []*parser.ParsedEvent{
		{
			Name: "name1",
			Data: map[string]interface{}{
				"action": "added",
				"columns": map[string]interface{}{
					"column1": "hello",
					"column2": 1.234,
				},
			},
		},
		{
			Name: "name1",
			Data: map[string]interface{}{
				"action": "added",
				"columns": map[string]interface{}{
					"column1": "world",
					"column2": 2.345,
				},
			},
		},
		{
			Name: "name2",
			Data: map[string]interface{}{
				"action": "added",
				"columns": map[string]interface{}{
					"column10": "hola",
				},
			},
		},
	}
	time1 := time.Unix(123456, 0)
	eventBatcher.AppendWithTimestamp(events1, time1)
	for name, batch := range eventBatcher.FlushAll() {
		err := sender.SubmitEvents(name, batch)
		require.NoError(t, err)
	}

	events2 := []*parser.ParsedEvent{
		{
			Name: "name1",
			Data: map[string]interface{}{
				"action": "removed",
				"columns": map[string]interface{}{
					"column1": "goodbye",
					"column4": 3.456,
				},
			},
		},
		{
			Name: "name1",
			Data: map[string]interface{}{
				"action": "added",
				"columns": map[string]interface{}{
					"column3": "world",
					"column2": 4.567,
				},
			},
		},
		{
			Name: "name2",
			Data: map[string]interface{}{
				"action": "removed",
				"columns": map[string]interface{}{
					"column11": "bueno",
				},
			},
		},
	}
	time2 := time.Unix(123457, 0)
	eventBatcher.AppendWithTimestamp(events2, time2)
	for name, batch := range eventBatcher.FlushAll() {
		err := sender.SubmitEvents(name, batch)
		require.NoError(t, err)
	}

	// Start() waits an arbitrary amount of time before running mergeDailyObjectsImpl, force running it.
	merger.mergeDailyObjectsImpl()

	sender.Stop()

	name1Data, err := s3Client.GetObjectWithContext(context.Background(), &awsS3.GetObjectInput{
		Bucket: &testBucket,
		Key:    aws.String("/name1/merged/1970-01-02.tsv.lz4"),
	})
	require.NoError(t, err)
	name1AllBytes, err := ioutil.ReadAll(lz4.NewReader(name1Data.Body))
	name1All := string(name1AllBytes)
	require.NoError(t, err)
	name1Expected := "timestamp\taction\thost\tcolumn1\tcolumn2\tcolumn3\tcolumn4\n" +
		"123456\tadded\t\thello\t1.234\t\t\n" +
		"123456\tadded\t\tworld\t2.345\t\t\n" +
		"123457\tremoved\t\tgoodbye\t0\t\t3.456\n" +
		"123457\tadded\t\t\t4.567\tworld\t0\n"
	require.Equal(t, name1Expected, name1All)

	name2Data, err := s3Client.GetObjectWithContext(context.Background(), &awsS3.GetObjectInput{
		Bucket: &testBucket,
		Key:    aws.String("/name2/merged/1970-01-02.tsv.lz4"),
	})
	require.NoError(t, err)
	name2AllBytes, err := ioutil.ReadAll(lz4.NewReader(name2Data.Body))
	name2All := string(name2AllBytes)
	require.NoError(t, err)
	name2Expected := "timestamp\taction\thost\tcolumn10\tcolumn11\n" +
		"123456\tadded\t\thola\t\n" +
		"123457\tremoved\t\t\tbueno\n"
	require.Equal(t, name2Expected, name2All)
}

func TestS3Large(t *testing.T) {
	s3Client := &s3ClientMock{
		t:        t,
		objects:  map[string][]byte{},
		metadata: map[string]map[string]*string{},
		uploads:  map[string]*mockUpload{},
	}

	manager := NewS3Manager(s3Client, &S3ManagerConfig{
		EnableDebug:        true,
		NumRetries:         10,
		NumDownloadWorkers: 4,
		NumUploadWorkers:   4,
		NumGetInfoWorkers:  4,
		MinUploadPartSize:  1000,
	})

	merger := &s3Merger{
		enableDebug:           true,
		bucket:                testBucket,
		manager:               manager,
		mergedAlg:             CompressionLz4,
		loc:                   time.UTC,
		deleteMergedAfterDays: 1,
		mergerLoad:            metrics.NewLoadReporter(time.Hour * 24),
	}

	// This is very hacked-up: we fill only the required fields in S3Sender.
	sender := &S3Sender{
		enableDebug: true,
		manager:     manager,
		bucket:      testBucket,
		alg:         CompressionSnappy,
		loc:         time.UTC,
		merger:      merger,
	}

	events11, events11Buf := generateEvents(10000, 0)
	err := sender.SubmitEvents("name1", events11)
	require.NoError(t, err)

	// events 2 should go after events1
	events12, events12Buf := generateEvents(20000, 10000)
	err = sender.SubmitEvents("name1", events12)
	require.NoError(t, err)
	events12Buf = cutHeader(events12Buf)

	events2, events2Buf := generateEvents(30000, 0)
	err = sender.SubmitEvents("name2", events2)
	require.NoError(t, err)

	// Start() waits an arbitrary amount of time before running mergeDailyObjectsImpl, force running it.
	merger.mergeDailyObjectsImpl()

	name1Data, err := s3Client.GetObjectWithContext(context.Background(), &awsS3.GetObjectInput{
		Bucket: &testBucket,
		Key:    aws.String("/name1/merged/1970-01-01.tsv.lz4"),
	})
	require.NoError(t, err)
	name1AllBytes, err := ioutil.ReadAll(lz4.NewReader(name1Data.Body))
	name1All := string(name1AllBytes)
	require.NoError(t, err)
	require.True(t, events11Buf+events12Buf == name1All)

	name2Data, err := s3Client.GetObjectWithContext(context.Background(), &awsS3.GetObjectInput{
		Bucket: &testBucket,
		Key:    aws.String("/name2/merged/1970-01-01.tsv.lz4"),
	})
	require.NoError(t, err)
	name2AllBytes, err := ioutil.ReadAll(lz4.NewReader(name2Data.Body))
	name2All := string(name2AllBytes)
	require.NoError(t, err)
	require.True(t, events2Buf == name2All)
}

func cutHeader(buf string) string {
	idx := strings.IndexByte(buf, '\n')
	return buf[idx+1:]
}
