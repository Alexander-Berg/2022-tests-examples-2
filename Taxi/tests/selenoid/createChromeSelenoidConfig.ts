import os from 'os'

import {WindowSize} from '../config'

interface ConfigProps {
  name: string
  windowSize?: WindowSize
}

const getConfigHostEntries = () => {
  /* на некоторых linux последний докер не резолвит корректно localhost без явного указания */
  if (os.type() === 'Linux') {
    return [`host.docker.internal:172.17.0.1`]
  }
  return undefined
}

export const createChromeSelenoidConfig = ({name, windowSize}: ConfigProps) => ({
  'selenoid:options': {
    enableVNC: !process.env.CI,
    enableVideo: false,
    enableLog: false,
    ...(windowSize ? {screenResolution: `${windowSize.width}x${windowSize.height}x24`} : undefined),
    /* Имя для отображения в selenoid-ui */
    name: name,
    hostsEntries: getConfigHostEntries(),
  },
})
