import React from "react";
import { Skeleton as BaseSkeleton, Stack } from "@yandex-fleet/signalq-fw-ui";

export default function Skeleton() {
  return (
    <Stack space="small">
      <BaseSkeleton animation="shimmer" shape="text" />
      <BaseSkeleton animation="shimmer" shape="text" />
    </Stack>
  );
}
