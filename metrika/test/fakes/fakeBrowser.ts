interface FakeBrowser {
  zoomLevel: number
  orientation: number
  viewport: Browser.Rect
  panels: {
    topPanel: boolean
    bottomPanel: boolean
  }
  mousePosition: Browser.Point
  mouseClicked: boolean
  touches: Map<string, TouchInfo>
  getTouches (): TouchInfo[]
}

interface TouchInfo extends Browser.Point {
  id: string
}

export default {
  viewport: {width: 0, height: 0},
  orientation: 0,
  zoomLevel: 1,
  panels: {
    topPanel: false,
    bottomPanel: false,
  },
  mousePosition: {
    x: 0,
    y: 0,
  },
  touches: new Map<string, TouchInfo>(),

  setViewportSize (viewport: Browser.Rect) {
    this.viewport = viewport
    return Promise.resolve()
  },

  setPanels (panels: any) {
    this.panels = {...panels}
  },

  setOrientation (rotation: number) {
    this.orientation = rotation
  },

  setZoomLevel (zoom: number) {
    this.zoomLevel = zoom
  },

  getZoomLevel () {
    return this.zoomLevel
  },

  setScrollPosition(position: Browser.Point) {
    return
  },

  setClickPosition (position: Browser.Point) {
    this.mouseClicked = true
    this.setMousePosition(position)
  },

  updateClickPosition (position: Browser.Point) {
    this.setMousePosition(position)
  },

  releaseClickPosition () {
    this.mouseClicked = false
  },

  addTouch (id: string, position: Browser.Point) {
    this.touches.set(id, {id, ...position})
  },

  moveTouch (id: string, position: Browser.Point) {
    const touch = this.touches.get(id)
    if (touch) {
      touch.x = position.x
      touch.y = position.y
      this.touches.set(id, touch)
    }
  },

  removeTouch (id: string) {
    this.touches.delete(id)
  },

  setMousePosition (position: Browser.Point) {
    this.mousePosition = position
  },

  getTouches () {
    return Array.from(this.touches.values())
  },

  reset () {
    this.touches.clear()
    this.zoomLevel = 1
    this.orientation = 0
    this.viewport = {width: 0, height: 0}
    this.panels = {
      topPanel: false,
      bottomPanel: false,
    }
    this.mousePosition = {
      x: 0,
      y: 0,
    }
  },
} as (FakeBrowser & Browser.Interface)
