/**
 * Reusable Alpine component for a photo gallery with prev/next navigation,
 * a numeric counter, thumbnails, and an optional full-screen lightbox.
 *
 * Loaded (deferred) before the Alpine vendor script in base.html so
 * `window.imageGallery` exists by the time Alpine evaluates any
 * `x-data="imageGallery(...)"` attribute — same load-order pattern as the
 * inline `tourBuilder()` component in tour_builder.html.
 *
 * `images` is a plain array of `{ url, alt }` objects built server-side in
 * the template (gallery photos are looked up once per request, not fetched
 * client-side).
 */
function imageGallery(images) {
  images = images || [];
  return {
    images: images,
    index: 0,
    lightboxOpen: false,
    get current() {
      return this.images[this.index];
    },
    next() {
      if (this.images.length < 2) return;
      this.index = (this.index + 1) % this.images.length;
    },
    prev() {
      if (this.images.length < 2) return;
      this.index = (this.index - 1 + this.images.length) % this.images.length;
    },
    goTo(i) {
      this.index = Math.max(0, Math.min(i, this.images.length - 1));
    },
    open(i) {
      this.goTo(i);
      this.lightboxOpen = true;
    },
    close() {
      this.lightboxOpen = false;
    },
  };
}
