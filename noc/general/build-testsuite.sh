make distclean
CXXFLAGS=-fPIC CPPLAGS=-fPIC CFLAGS=-fPIC ./configure \
  --enable-shared \
  --enable-epoll \
  --disable-video \
  --disable-sound \
  --disable-g711-codec \
  --disable-openh264 \
  --disable-ffmpeg \
  --disable-ilbc-codec \
  --disable-v4l2 \
  --disable-opus \
  --disable-g722-codec \
  --disable-speex-codec \
  --disable-opencore-amr \
  --disable-oss \
  --disable-speex-aec \
  --disable-gsm-codec \
  --disable-silk \
  --disable-libyuv
make dep
make
make install

cd pjsip-apps/src/swig
make distclean
make python
make install

