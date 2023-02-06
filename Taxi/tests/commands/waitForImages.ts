const WAIT_FOR_IMAGES_ITERATION_PAUSE = 200
const WAIT_FOR_IMAGES_TOTAL_TIME = 20000

export async function waitForImages(
  this: WebdriverIO.Browser,
  options: {
    testId: string
  },
  iterationData = {
    successIterations: 0,
    timeLeft: WAIT_FOR_IMAGES_TOTAL_TIME,
    prevImagesCount: 0,
  },
) {
  const {successIterations, prevImagesCount, timeLeft} = iterationData
  let nextSuccessIterations = successIterations
  const {imagesCount, hasNotLoadedImage, imageCountChanged} = await this.execute(
    ({prevImagesCount, testId}) => {
      const images = Array.from(document.images).filter(image => {
        if (testId) {
          return image.getAttribute('data-testid') === testId
        }
        return true
      })
      const imagesCount = images.length
      if (prevImagesCount && prevImagesCount !== imagesCount) {
        return {imageCountChanged: true, imagesCount}
      }
      for (let i = 0; i < imagesCount; i++) {
        if (!images[i].complete) {
          return {
            hasNotLoadedImage: true,
            imagesCount,
          }
        }
      }
      return {imagesCount}
    },
    {testId: options?.testId, prevImagesCount},
  )
  if (imageCountChanged) {
    nextSuccessIterations = 0
  }
  if (!hasNotLoadedImage && !imageCountChanged) {
    nextSuccessIterations += 1
  }

  if (nextSuccessIterations === 3) {
    return true
  }

  const nextTimeLeft = timeLeft - WAIT_FOR_IMAGES_ITERATION_PAUSE

  if (nextTimeLeft < 0) {
    throw new Error(`Error from waitForImages. Waiting limit ${WAIT_FOR_IMAGES_TOTAL_TIME}ms has reached`)
  }
  await this.pause(WAIT_FOR_IMAGES_ITERATION_PAUSE)
  await waitForImages.call(this, options, {
    prevImagesCount: imagesCount,
    successIterations: nextSuccessIterations,
    timeLeft: nextTimeLeft,
  })
}
export type WaitForImages = typeof waitForImages
