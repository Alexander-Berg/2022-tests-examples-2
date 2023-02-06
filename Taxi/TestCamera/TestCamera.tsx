import React, { useState } from "react";
import {
  Stack,
  Button,
  Text,
  Columns,
  Column,
  useAlerts,
} from "@yandex-fleet/signalq-fw-ui";

import { useTranslation } from "../../i18n";
import { useDeleteTestRecords, useExternalCameraStatus } from "../../api/media";

import Photo from "./Photo";
import Video from "./Video";

export type FilePaths = { path: string; previewPath: string };

export type Files = {
  photo?: {
    external?: FilePaths;
    internal?: FilePaths;
  };
  video?: {
    external?: FilePaths;
    internal?: FilePaths;
  };
};

function Media({
  mediaType,
  cameraType,
  file,
  setIsDeleteDisabled,
  setFiles,
}: {
  mediaType: "photo" | "video";
  cameraType: "internal" | "external";
  file?: FilePaths;
  setIsDeleteDisabled: (value: boolean) => void;
  setFiles: (value?: Files | ((prevValue?: Files) => Files)) => void;
}) {
  const onDownloadClick = (path?: string) => {
    if (!path) return;

    const a = document.createElement("a");
    const fileName = path.split("/").reverse()[0]!;

    a.download = fileName;
    a.href = path;
    a.click();
  };

  switch (mediaType) {
    case "photo":
      return (
        <Photo
          channel={cameraType === "external" ? 1 : 0}
          onDownloadClick={onDownloadClick}
          file={file}
          setFile={(file?: FilePaths) =>
            setFiles((prev?: Files) => ({
              ...prev,
              photo: {
                ...prev?.photo,
                [cameraType]:
                  file?.path && file.previewPath
                    ? {
                        path: file.path,
                        previewPath: file.previewPath,
                      }
                    : undefined,
              },
            }))
          }
        />
      );
    case "video":
      return (
        <Video
          channel={cameraType === "external" ? 1 : 0}
          onDownloadClick={onDownloadClick}
          setIsDeleteDisabled={setIsDeleteDisabled}
          file={file}
          setFile={(file?: FilePaths) =>
            setFiles((prev?: Files) => ({
              ...prev,
              video: {
                ...prev?.video,
                [cameraType]:
                  file?.path && file.previewPath
                    ? {
                        path: file.path,
                        previewPath: file.previewPath,
                      }
                    : undefined,
              },
            }))
          }
        />
      );
  }
}

function Section({
  mediaType,
  isExternalCameraAvailable,
  setIsDeleteDisabled,
  files,
  setFiles,
}: {
  mediaType: "photo" | "video";
  isExternalCameraAvailable?: boolean;
  setIsDeleteDisabled: (value: boolean) => void;
  files?: Files["photo"] | Files["video"];
  setFiles: (value?: Files | ((prevValue?: Files) => Files)) => void;
}) {
  const { t } = useTranslation("test_camera");

  return (
    <Stack space="medium">
      <Text typography="headline1" color="main">
        {mediaType === "photo" ? t("test_photo.title") : t("test_video.title")}
      </Text>

      <Columns>
        <Column>
          <Stack space="xsmall">
            <Text typography="headline2" color="main">
              {t("external.title")}
            </Text>
            {isExternalCameraAvailable ? (
              <Media
                mediaType={mediaType}
                cameraType="external"
                file={files?.external}
                setIsDeleteDisabled={setIsDeleteDisabled}
                setFiles={setFiles}
              />
            ) : (
              <Text typography="body">{t("external.not_connected")}</Text>
            )}
          </Stack>
        </Column>

        <Column>
          <Stack space="small">
            <Text typography="headline2" color="main">
              {t("internal.title")}
            </Text>

            <Media
              mediaType={mediaType}
              cameraType="internal"
              file={files?.internal}
              setIsDeleteDisabled={setIsDeleteDisabled}
              setFiles={setFiles}
            />
          </Stack>
        </Column>
      </Columns>
    </Stack>
  );
}

export default function CameraTest() {
  const [isDeleteDisabled, setIsDeleteDisabled] = useState(false);
  const [files, setFiles] = useState<Files>();

  const { t } = useTranslation("test_camera");
  const { openAlert } = useAlerts();

  const { data: isExternalCameraAvailable } = useExternalCameraStatus({
    suspense: true,
    useErrorBoundary: true,
  });

  const { mutate: deleteRecords, isLoading: isDeleting } = useDeleteTestRecords(
    {
      onSuccess: ({ result }) => {
        if (result) setFiles(undefined);
        else openAlert({ text: t("delete_records.error") });
      },
      useErrorBoundary: true,
    }
  );

  const anyFileExists = Boolean(
    files?.photo?.external?.path ||
      files?.photo?.internal?.path ||
      files?.video?.external?.path ||
      files?.video?.internal?.path
  );

  return (
    <Stack space="xlarge">
      <Section
        mediaType="photo"
        isExternalCameraAvailable={isExternalCameraAvailable}
        setIsDeleteDisabled={setIsDeleteDisabled}
        files={files?.photo}
        setFiles={setFiles}
      />
      <Section
        mediaType="video"
        isExternalCameraAvailable={isExternalCameraAvailable}
        setIsDeleteDisabled={setIsDeleteDisabled}
        files={files?.video}
        setFiles={setFiles}
      />

      <Button
        view="default"
        onClick={() => deleteRecords()}
        disabled={isDeleteDisabled || !anyFileExists}
        progress={isDeleting}
      >
        {t("delete_records.action")}
      </Button>
    </Stack>
  );
}
