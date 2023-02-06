import Defer from '@tips/ui-kit/lib/defer'
import {ImageScheduler} from '.'

jest.useRealTimers()

describe('lib', () => {
  describe('ImageScheduler', () => {
    let images: MockImage[] = []

    class MockImage {
      static onCreate(fn: (image: MockImage) => void) {
        this._onCreate = fn
      }

      private static _onCreate = (_image: MockImage) => {
        // noop
      }

      src = ''
      onload: ((e: Event) => any) | null = null
      onerror: ((e: ErrorEvent) => any) | null = null

      constructor() {
        images.push(this)
        MockImage._onCreate(this)
      }

      $resolve() {
        this.onload!({} as any)
      }

      $reject() {
        this.onerror!({} as any)
      }
    }

    function mockImageLoader(src: string): Promise<void> {
      return new Promise((resolve, reject) => {
        const image = new MockImage()

        image.src = src
        image.onload = (_event) => resolve()
        image.onerror = reject
      })
    }

    let imageScheduler: ImageScheduler

    beforeEach(() => {
      images = []
      MockImage.onCreate(() => {
        // noop
      })
      imageScheduler = new ImageScheduler(mockImageLoader)
    })

    describe('queueLenght', () => {
      it('should work', () => {
        expect(imageScheduler.queueLenght).toEqual(0)
      })

      it('should be incremented when task added into the queue', () => {
        expect(imageScheduler.queueLenght).toEqual(0)
        imageScheduler.add('http://localhost/img.jpg')
        expect(imageScheduler.queueLenght).toEqual(1)
      })

      it('should be decremented when task removed from the queue', () => {
        expect(imageScheduler.queueLenght).toEqual(0)
        imageScheduler.add('http://localhost/img.jpg')
        expect(imageScheduler.queueLenght).toEqual(1)
        imageScheduler.remove('http://localhost/img.jpg')
        expect(imageScheduler.queueLenght).toEqual(0)
      })
    })

    describe('add', () => {
      it('should work', () => {
        imageScheduler.add('http://localhost/img.jpg')
      })
    })

    describe('remove', () => {
      it('should work', () => {
        imageScheduler.add('http://localhost/img.jpg')
        imageScheduler.remove('http://localhost/img.jpg')
      })

      it('should remove items from the queue', () => {
        expect(imageScheduler.queueLenght).toEqual(0)

        imageScheduler.add('http://localhost/img-1.jpg')
        expect(imageScheduler.queueLenght).toEqual(1)
        imageScheduler.add('http://localhost/img-2.jpg')
        expect(imageScheduler.queueLenght).toEqual(2)
        imageScheduler.add('http://localhost/img-3.jpg')
        expect(imageScheduler.queueLenght).toEqual(3)
        imageScheduler.add('http://localhost/img-4.jpg')
        expect(imageScheduler.queueLenght).toEqual(4)
        imageScheduler.add('http://localhost/img-5.jpg')
        expect(imageScheduler.queueLenght).toEqual(5)
        imageScheduler.add('http://localhost/img-6.jpg')
        expect(imageScheduler.queueLenght).toEqual(6)
        imageScheduler.add('http://localhost/img-7.jpg')
        expect(imageScheduler.queueLenght).toEqual(7)
        imageScheduler.add('http://localhost/img-8.jpg')
        expect(imageScheduler.queueLenght).toEqual(8)
        imageScheduler.add('http://localhost/img-9.jpg')
        expect(imageScheduler.queueLenght).toEqual(9)

        imageScheduler.remove('http://localhost/img-7.jpg')
        expect(imageScheduler.queueLenght).toEqual(8)
        imageScheduler.remove('http://localhost/img-2.jpg')
        expect(imageScheduler.queueLenght).toEqual(7)
        imageScheduler.remove('http://localhost/img-9.jpg')
        expect(imageScheduler.queueLenght).toEqual(6)
        imageScheduler.remove('http://localhost/img-4.jpg')
        expect(imageScheduler.queueLenght).toEqual(5)
        imageScheduler.remove('http://localhost/img-5.jpg')
        expect(imageScheduler.queueLenght).toEqual(4)
        imageScheduler.remove('http://localhost/img-1.jpg')
        expect(imageScheduler.queueLenght).toEqual(3)
        imageScheduler.remove('http://localhost/img-6.jpg')
        expect(imageScheduler.queueLenght).toEqual(2)
        imageScheduler.remove('http://localhost/img-8.jpg')
        expect(imageScheduler.queueLenght).toEqual(1)
        imageScheduler.remove('http://localhost/img-3.jpg')
        expect(imageScheduler.queueLenght).toEqual(0)
      })
    })

    describe('register', () => {
      it('should work', () => {
        imageScheduler.register('http://localhost/img.jpg')
      })

      it('should return passed URL', () => {
        const url = imageScheduler.register('http://localhost/img.jpg')

        expect(url).toBe('http://localhost/img.jpg')
      })
    })

    describe('start', () => {
      it('should work', () => {
        imageScheduler.start()
      })

      it('should start loading images', async () => {
        imageScheduler.add('http://localhost/img-1337.jpg')

        expect(images).toHaveLength(0)
        expect(imageScheduler.queueLenght).toEqual(1)

        const defer = new Defer<void>()

        MockImage.onCreate((image) => {
          setTimeout(() => {
            image.$resolve()
            defer.resolve()
          })
        })

        imageScheduler.start()

        await defer.promise

        expect(images).toHaveLength(1)
        expect(images.map((img) => img.src)).toEqual(['http://localhost/img-1337.jpg'])
        expect(imageScheduler.queueLenght).toEqual(0)
      })

      it('should load images in order', async () => {
        imageScheduler.add('http://localhost/img-1.jpg')
        imageScheduler.add('http://localhost/img-2.jpg')
        imageScheduler.add('http://localhost/img-3.jpg')
        imageScheduler.add('http://localhost/img-4.jpg')
        imageScheduler.add('http://localhost/img-5.jpg')
        imageScheduler.add('http://localhost/img-6.jpg')
        imageScheduler.add('http://localhost/img-7.jpg')
        imageScheduler.add('http://localhost/img-8.jpg')
        imageScheduler.add('http://localhost/img-9.jpg')

        expect(images).toHaveLength(0)
        expect(imageScheduler.queueLenght).toEqual(9)

        let count = 0
        const defer = new Defer<void>()

        MockImage.onCreate((image) => {
          setTimeout(() => {
            count++

            image.$resolve()

            if (count === 9) {
              defer.resolve()
            }
          })
        })

        imageScheduler.start()

        await defer.promise

        expect(images).toHaveLength(9)
        expect(images.map((img) => img.src)).toEqual([
          'http://localhost/img-1.jpg',
          'http://localhost/img-2.jpg',
          'http://localhost/img-3.jpg',
          'http://localhost/img-4.jpg',
          'http://localhost/img-5.jpg',
          'http://localhost/img-6.jpg',
          'http://localhost/img-7.jpg',
          'http://localhost/img-8.jpg',
          'http://localhost/img-9.jpg',
        ])
        expect(imageScheduler.queueLenght).toEqual(0)
      })

      it('should load images with higher priority before others', async () => {
        imageScheduler.add('http://localhost/img-1.jpg', 100)
        imageScheduler.add('http://localhost/img-2.jpg', 200)
        imageScheduler.add('http://localhost/img-3.jpg', 300)
        imageScheduler.add('http://localhost/img-4.jpg', 400)
        imageScheduler.add('http://localhost/img-5.jpg', 500)

        expect(images).toHaveLength(0)
        expect(imageScheduler.queueLenght).toEqual(5)

        let count = 0
        const defer = new Defer<void>()

        MockImage.onCreate((image) => {
          setTimeout(() => {
            count++

            image.$resolve()

            if (count === 5) {
              defer.resolve()
            }
          })
        })

        imageScheduler.start()

        await defer.promise

        expect(images).toHaveLength(5)
        expect(images.map((img) => img.src)).toEqual([
          'http://localhost/img-5.jpg',
          'http://localhost/img-4.jpg',
          'http://localhost/img-3.jpg',
          'http://localhost/img-2.jpg',
          'http://localhost/img-1.jpg',
        ])
        expect(imageScheduler.queueLenght).toEqual(0)
      })
    })
  })
})
