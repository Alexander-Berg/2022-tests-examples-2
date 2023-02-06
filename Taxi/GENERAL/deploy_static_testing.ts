import * as fs from "fs/promises";
import * as path from "path";
import * as mime from "mime-types";
import * as s3 from "@aws-sdk/client-s3";
import { fdir as Fdir } from "fdir";

const crawlSync = (dir: string) =>
  new Fdir().withBasePath().crawl(dir).sync() as string[];

const main = async () => {
  const client = new s3.S3Client({
    region: "REGION",
    endpoint: "http://s3.mdst.yandex.net",
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID ?? "",
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY ?? "",
    },
  });

  // Files that can be cached forever
  const isStatic = (p: string) =>
    /^fleet\/(yandex|yandex-team|uber)\/static\/.+/.test(p);

  // index.html files
  const isIndex = (p: string) =>
    /^fleet\/(yandex|yandex-team|uber)\/index\.html\/.+/.test(p);

  const prevObjects = [] as s3._Object[];

  for (;;) {
    const nextMarker = prevObjects.length
      ? prevObjects[prevObjects.length - 1].Key
      : undefined;

    const { Contents, IsTruncated = false } = await client.send(
      new s3.ListObjectsCommand({
        Bucket: "fleet-web",
        Prefix: "fleet/",
        Marker: nextMarker,
      })
    );

    if (Contents) {
      prevObjects.push(...Contents);
    }

    if (!IsTruncated) {
      break;
    }
  }

  const prevFiles = prevObjects
    .map((o) => o.Key?.slice(6) ?? "")
    .filter((p) => p);
  const nextFiles = crawlSync("dist").map((f) => path.relative("dist", f));

  const staticFiles = nextFiles.filter((f) => isStatic(f));
  const noCacheFiles = nextFiles.filter((f) => !isStatic(f) && !isIndex(f));
  const indexFiles = nextFiles.filter((f) => isIndex(f));

  const upload = async (f: string, cache: string) => {
    return client.send(
      new s3.PutObjectCommand({
        Bucket: "fleet-web",
        Key: path.join("fleet", f).replace(/\\/g, "/"),
        Body: await fs.readFile(path.join("dist", f)),
        ContentType: mime.lookup(f) || undefined,
        CacheControl: cache,
      })
    );
  };

  // First upload non-index files
  for (const file of staticFiles) {
    await upload(file, "max-age=31536000");
  }

  for (const file of noCacheFiles) {
    await upload(file, "no-cache");
  }

  // Then uplopad index.html's
  for (const file of indexFiles) {
    await upload(file, "no-cache");
  }

  // Finally remove unneeded
  for (const file of prevFiles) {
    if (!nextFiles.includes(file)) {
      await client.send(
        new s3.DeleteObjectCommand({
          Bucket: "fleet-web",
          Key: path.join("fleet", file).replace(/\\/g, "/"),
        })
      );
    }
  }

  console.log("Successfully deployed");
};

void main();
