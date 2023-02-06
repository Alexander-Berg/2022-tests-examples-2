import React, { useState, useEffect } from "react";

import {
  Modal as BaseModal,
  ModalAction,
  ModalActions,
  Text,
  Stack,
  Slider,
  Textinput,
} from "@yandex-fleet/signalq-fw-ui";

import { useTranslation } from "../../i18n";

import styles from "./styles.module.css";

export type Settings = { recordingLength: number; preRecordingLength: number };

function Field({
  value,
  onChange,
}: {
  value: Settings["preRecordingLength"] | Settings["recordingLength"];
  onChange: <T extends keyof Settings>(value: Settings[T]) => void;
}) {
  return (
    <div className={styles["field"]}>
      <Slider
        view="default"
        min={1}
        max={60}
        filled
        value={[value]}
        onInput={(_: unknown, [v]: number[]) => onChange(v!)}
      />
      <Textinput
        type="number"
        min={1}
        max={60}
        value={value}
        view="outline"
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}

type Props = {
  visible: boolean;
  onAccept: (settings: Settings) => void;
  onClose: () => void;
  isLoading?: boolean;
};

export default function Modal({
  visible,
  onAccept,
  onClose,
  isLoading,
}: Props) {
  const { t } = useTranslation("test_camera");

  const [settings, setSettings] = useState<Settings>({
    recordingLength: 1,
    preRecordingLength: 1,
  });

  const onChange = <T extends keyof Settings>(field: T, value: Settings[T]) =>
    setSettings((prev) => ({ ...prev, [field]: value }));

  useEffect(() => {
    if (!visible) setSettings({ recordingLength: 1, preRecordingLength: 1 });
  }, [visible]);

  return (
    <BaseModal title={t("modal.title")} visible={visible} onClose={onClose}>
      <Stack space="xlarge">
        <Stack space="xsmall">
          <Text typography="body">{t("modal.length.label")}</Text>
          <Field
            value={settings.recordingLength}
            onChange={(value) => onChange("recordingLength", value)}
          />
        </Stack>

        <Stack space="xsmall">
          <Text typography="body">{t("modal.pre.label")}</Text>

          <Field
            value={settings.preRecordingLength}
            onChange={(value) => onChange("preRecordingLength", value)}
          />
        </Stack>

        <ModalActions>
          <ModalAction actionType="cancel" onClick={onClose}>
            {t("modal.cancel")}
          </ModalAction>

          <ModalAction
            actionType="accept"
            progress={isLoading}
            onClick={() =>
              onAccept({
                recordingLength: settings.recordingLength,
                preRecordingLength: settings.preRecordingLength,
              })
            }
          >
            {t("modal.accept")}
          </ModalAction>
        </ModalActions>
      </Stack>
    </BaseModal>
  );
}
