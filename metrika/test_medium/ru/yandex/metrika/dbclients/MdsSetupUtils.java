package ru.yandex.metrika.dbclients;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;

import ru.yandex.metrika.dbclients.config.MdsTestConfig;

public class MdsSetupUtils {

    public static String arcadiaEndpointUrl() {
        return "http://127.0.0.1:" + System.getenv("S3MDS_PORT");
    }

    public static String arcadiaFakeAccessKey() {
        return "fake_access_key";
    }

    public static String arcadiaFakeAccessToken() {
        return "fake_access_token";
    }

    public static MdsTestConfig arcadiaConfig() {
        return new MdsTestConfig(arcadiaEndpointUrl(), arcadiaFakeAccessKey(), arcadiaFakeAccessToken());
    }

    public static void createBucket(MdsTestConfig config, String bucketName) {
        AwsClientBuilder.EndpointConfiguration endpointConfiguration = new AwsClientBuilder.EndpointConfiguration(
                config.getEndpoint(), Regions.US_EAST_1.getName());
        AWSCredentials credentials = new BasicAWSCredentials(config.getAccessKey(), config.getSecretKey());
        AWSCredentialsProvider credentialsProvider = new AWSStaticCredentialsProvider(credentials);
        AmazonS3 client = AmazonS3ClientBuilder
                .standard()
                .disableChunkedEncoding()
                .withDualstackEnabled(false)
                .withCredentials(credentialsProvider)
                .withEndpointConfiguration(endpointConfiguration)
                .build();

        client.createBucket(bucketName);
    }
}
