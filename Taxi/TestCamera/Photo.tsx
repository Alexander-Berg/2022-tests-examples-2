import React, { useState } from "react";
import {
  Stack,
  Button,
  Preview,
  Image,
  MediaBadges,
  useAlerts,
} from "@yandex-fleet/signalq-fw-ui";

import { useTranslation } from "../../i18n";
import {
  usePhoto,
  usePhotoFilePath,
  type UsePhotoParams,
} from "../../api/media";

import File from "../File";
import Skeleton from "./Skeleton";

import type { FilePaths } from "./TestCamera";

interface Props {
  channel: UsePhotoParams["channel"];
  onDownloadClick: (path?: string) => void;
  file?: FilePaths;
  setFile: (value?: FilePaths) => void;
}

export default function Photo({
  channel,
  onDownloadClick,
  file,
  setFile,
}: Props) {
  const { t } = useTranslation("test_camera");
  const { openAlert } = useAlerts();

  const [isImageOpened, setIsImageOpened] = useState(false);

  const { mutate: takePhoto } = usePhoto({
    onSuccess: (data) => {
      if (data.result) {
        setFile(undefined);
        void refetchFilePath();
      } else openAlert({ text: t("take_photo.error") });
    },
    useErrorBoundary: true,
  });

  const { refetch: refetchFilePath, isLoading: isLoadingPhoto } =
    usePhotoFilePath(
      { channel },
      {
        onSettled: (data) => {
          if (!data?.result) return setFile(undefined);

          return setFile({
            path: data.pic_file,
            previewPath: `${data.pic_file}?=${Math.floor(
              Math.random() * 10000
            )}`,
          });
        },
      }
    );

  return (
    <Stack space="small">
      {isLoadingPhoto ? (
        <Skeleton />
      ) : (
        <>
          {file?.path && (
            <File
              name={file.path}
              onFileClick={() => setIsImageOpened(true)}
              onDownloadClick={() => onDownloadClick(file.path)}
            />
          )}

          <Button view="default" onClick={() => takePhoto({ channel })}>
            {file ? t("take_photo.retake.action") : t("take_photo.action")}
          </Button>
        </>
      )}

      {file?.previewPath && (
        <Preview
          onBackdropClick={() => setIsImageOpened(false)}
          visible={isImageOpened}
          zIndex={1000}
        >
          <Image
            src={file.previewPath}
            badges={
              <MediaBadges onDownloadClick={() => onDownloadClick(file.path)} />
            }
          />
        </Preview>
      )}
    </Stack>
  );
}
