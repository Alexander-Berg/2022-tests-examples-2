import React, { useState } from "react";
import {
  Stack,
  Button,
  Preview,
  Video as BaseVideo,
  MediaBadges,
  useAlerts,
} from "@yandex-fleet/signalq-fw-ui";

import { useTranslation } from "../../i18n";
import {
  useRecordingStatus,
  useVideoFilePath,
  useVideo,
  type UsePhotoParams,
} from "../../api/media";
import { useAppConfig } from "../../app-config";

import File from "../File";
import Modal from "./Modal";
import Skeleton from "./Skeleton";

import type { Settings } from "./Modal";
import type { FilePaths } from "./TestCamera";

interface Props {
  channel: UsePhotoParams["channel"];
  onDownloadClick: (path?: string) => void;
  setIsDeleteDisabled: (value: boolean) => void;
  file?: FilePaths;
  setFile: (value?: FilePaths) => void;
}

export default function Video({
  channel,
  onDownloadClick,
  setIsDeleteDisabled,
  file,
  setFile,
}: Props) {
  const { openAlert } = useAlerts();
  const { t } = useTranslation("test_camera");
  const { data: config } = useAppConfig();

  const [refetchInterval, setRefetchInterval] = useState<number>();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isVideoOpened, setIsVideoOpened] = useState(false);

  const { data: isRecording, refetch: refetchRecordingStatus } =
    useRecordingStatus(
      { channel },
      {
        onSuccess: (isRecording) => {
          if (isRecording) {
            setRefetchInterval(config?.refetch_intervals?.test_camera ?? 500);
            setIsDeleteDisabled(true);
          } else {
            setRefetchInterval(undefined);
            void refetchFilePath();
            setIsDeleteDisabled(false);
          }
        },
        refetchInterval,
        refetchIntervalInBackground: true,
        useErrorBoundary: true,
      }
    );

  const { refetch: refetchFilePath, isLoading: isLoadingVideo } =
    useVideoFilePath(
      { channel },
      {
        onSettled: (data) => {
          if (data?.result)
            setFile({
              path: data.file,
              previewPath: `${data.file}?=${Math.floor(Math.random() * 10000)}`,
            });
          else setFile(undefined);
        },
      }
    );

  const { mutate: recordVideo } = useVideo({
    onSuccess: ({ result }) => {
      if (result) {
        setFile(undefined);
        setIsModalVisible(false);
        void refetchRecordingStatus();
      } else openAlert({ text: t("record_video.error") });
    },
    useErrorBoundary: true,
  });

  const onAccept = ({ recordingLength, preRecordingLength }: Settings) =>
    recordVideo({ channel, length: recordingLength, pre: preRecordingLength });

  const getButtonLabel = () => {
    if (isRecording) return t("record_video.is_recording");
    if (file?.path) return t("record_video.re-record.action");
    return t("record_video.action");
  };

  return (
    <Stack space="small">
      {isLoadingVideo ? (
        <Skeleton />
      ) : (
        <>
          {file?.path && (
            <File
              name={file.path}
              onFileClick={() => setIsVideoOpened(true)}
              onDownloadClick={() => onDownloadClick(file.path)}
            />
          )}

          <Button
            view="default"
            progress={Boolean(isRecording)}
            disabled={Boolean(isRecording)}
            onClick={() => setIsModalVisible(true)}
          >
            {getButtonLabel()}
          </Button>
        </>
      )}

      {file?.previewPath && (
        <Preview
          onBackdropClick={() => setIsVideoOpened(false)}
          visible={isVideoOpened}
          zIndex={1000}
        >
          <BaseVideo
            src={file.previewPath}
            errorMessage={t("video.error")}
            badges={
              <MediaBadges onDownloadClick={() => onDownloadClick(file.path)} />
            }
          />
        </Preview>
      )}

      <Modal
        visible={isModalVisible}
        onAccept={onAccept}
        onClose={() => setIsModalVisible(false)}
      />
    </Stack>
  );
}
