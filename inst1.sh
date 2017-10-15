#!/bin/bash
# export PYTHONVERBOSE=0
export QT_API=pyqt5
pyinstaller -y -d --log-level=DEBUG old.yams.spec
rm -r dist/yams/share/icons
rm -r dist/yams/share/locale
rm -r dist/yams/mpl-data/sample_data
mv dist/yams/mpl-data/images dist/yams/mpl-data/images_x
mkdir dist/yams/mpl-data/images
cp dist/yams/mpl-data/images_x/matplotlib.svg dist/yams/mpl-data/images
#cp dist/yams/mpl-data/images_x/svg+xml.xml dist/yams/mpl-data/images
rm -r dist/yams/mpl-data/images_x
rm -r dist/yams/share/fontconfig
rm -r dist/yams/share/themes
rm -r dist/yams/PyQt5/Qt/plugins/iconengines
rm -r dist/yams/PyQt5/Qt/plugins/imageformats
rm -r dist/yams/PyQt5/Qt/plugins/platformthemes
rm -r dist/yams/PyQt5/Qt/plugins/printsupport
rm -r dist/yams/pytz
rm -r dist/yams/tcl/encoding
# rm dist/yams/liblapack.so.3
rm dist/yams/libgtk-3.so.0
#rm dist/yams/libatlas.so.3
rm dist/yams/libcrypto.so.1.1
rm dist/yams/libQt5Network.so.5
# rm dist/yams/libgfortran.so.3
rm dist/yams/libsqlite3.so.0
rm dist/yams/libcairo.so.2
rm dist/yams/libepoxy.so.0
rm dist/yams/libgcrypt.so.20
rm dist/yams/libkrb5.so.3
#rm dist/yams/libtcl8.6.so
rm dist/yams/_codecs_jp.so
#rm dist/yams/libblas.so.3
rm dist/yams/libblkid.so.1
#rm dist/yams/libBLT.2.5.so.8.6
rm dist/yams/libcups.so.2
rm dist/yams/libEGL.so.1
rm dist/yams/libfontconfig.so.1
rm dist/yams/libfreetype.so.6
rm dist/yams/libgdk-3.so.0
rm dist/yams/libgio-2.0.so.0
rm dist/yams/libgnutls.so.30
rm dist/yams/libgssapi_krb5.so.2
rm dist/yams/libgvfscommon.so
rm dist/yams/libharfbuzz.so.0
rm dist/yams/libhogweed.so.4
rm dist/yams/libjpeg.so.62
rm dist/yams/libmount.so.1
rm dist/yams/libmpdec.so.2
rm dist/yams/libnettle.so.6
rm dist/yams/libp11-kit.so.0
rm dist/yams/libpango-1.0.so.0
rm dist/yams/libpgm-5.2.so.0
rm dist/yams/libpixman-1.so.0
rm dist/yams/libsodium.so.18
rm dist/yams/libssl.so.1.1
rm dist/yams/libstdc++.so.6
rm dist/yams/libtcl8.6.so
rm dist/yams/libtiff.so.5
rm dist/yams/libwebp.so.6
rm dist/yams/libzmq.so.5
rm dist/yams/_codecs_cn.so
rm dist/yams/_codecs_hk.so
rm dist/yams/_codecs_iso2022.so
rm dist/yams/_codecs_kr.so
rm dist/yams/_codecs_tw.so
rm dist/yams/_curses.so
rm dist/yams/_decimal.so
rm dist/yams/_hashlib.so
rm dist/yams/_json.so
rm dist/yams/_lsprof.so
rm dist/yams/_lzma.so
rm dist/yams/markupsafe._speedups.so
rm dist/yams/_multibytecodec.so
rm dist/yams/_opcode.so
rm dist/yams/readline.so
rm dist/yams/scipy.interpolate.dfitpack.so
rm dist/yams/scipy.interpolate._fitpack.so
rm dist/yams/scipy.interpolate.interpnd.so
rm dist/yams/scipy.interpolate._ppoly.so
rm dist/yams/scipy.linalg._flinalg.so
rm dist/yams/scipy.spatial.ckdtree.so
rm dist/yams/scipy.spatial._distance_wrap.so
rm dist/yams/scipy.spatial.qhull.so
rm dist/yams/scipy.stats.mvn.so
rm dist/yams/scipy.stats.statlib.so
rm dist/yams/scipy.stats._stats.so
rm dist/yams/sklearn.metrics.cluster.expected_mutual_info_fast.so
rm dist/yams/sklearn.metrics.pairwise_fast.so
rm dist/yams/sklearn.utils.lgamma.so
rm dist/yams/sklearn.utils.weight_vector.so
rm dist/yams/_sqlite3.so
rm dist/yams/_ssl.so
rm dist/yams/termios.so
rm dist/yams/tornado.speedups.so
rm dist/yams/_bz2.so
rm dist/yams/gi._gi.so
rm dist/yams/libatk-1.0.so.0
rm dist/yams/libatk-bridge-2.0.so.0
rm dist/yams/libatspi.so.0
rm dist/yams/libavahi-client.so.3
rm dist/yams/libavahi-common.so.3
rm dist/yams/libbsd.so.0
rm dist/yams/libbz2.so.1.0
rm dist/yams/libcairo-gobject.so.2
rm dist/yams/libcom_err.so.2
rm dist/yams/libdatrie.so.1
rm dist/yams/libdbus-1.so.3
rm dist/yams/libdrm.so.2
rm dist/yams/libexpat.so.1
rm dist/yams/libffi.so.6
rm dist/yams/libgbm.so.1
rm dist/yams/libgcc_s.so.1
rm dist/yams/libgdk_pixbuf-2.0.so.0
rm dist/yams/libgirepository-1.0.so.1
rm dist/yams/libglapi.so.0
rm dist/yams/libglib-2.0.so.0
rm dist/yams/libgmodule-2.0.so.0
rm dist/yams/libgmp.so.10
rm dist/yams/libgobject-2.0.so.0
rm dist/yams/libgpg-error.so.0
rm dist/yams/libgraphite2.so.3
rm dist/yams/libgthread-2.0.so.0
rm dist/yams/libICE.so.6
rm dist/yams/libidn.so.11
rm dist/yams/libjbig.so.0
rm dist/yams/libk5crypto.so.3
rm dist/yams/libkeyutils.so.1
rm dist/yams/libkrb5support.so.0
rm dist/yams/liblz4.so.1
rm dist/yams/liblzma.so.5
rm dist/yams/libncursesw.so.5
rm dist/yams/libpangocairo-1.0.so.0
rm dist/yams/libpangoft2-1.0.so.0
rm dist/yams/libpcre.so.3
#rm dist/yams/libpng16.so.16
rm dist/yams/libproxy.so.1
#rm dist/yams/libQt5DBus.so.5
rm dist/yams/libQt5PrintSupport.so.5
#rm dist/yams/libQt5Svg.so.5
rm dist/yams/libQt5X11Extras.so.5
#rm dist/yams/libQt5XcbQpa.so.5
rm dist/yams/libquadmath.so.0
rm dist/yams/libreadline.so.7
rm dist/yams/libselinux.so.1
rm dist/yams/libSM.so.6
rm dist/yams/libsystemd.so.0
rm dist/yams/libtasn1.so.6
rm dist/yams/libthai.so.0
rm dist/yams/libtinfo.so.5
rm dist/yams/libtk8.6.so
rm dist/yams/libuuid.so.1
rm dist/yams/libwayland-client.so.0
rm dist/yams/libwayland-cursor.so.0
rm dist/yams/libwayland-egl.so.1
rm dist/yams/libwayland-server.so.0
rm dist/yams/libwebpdemux.so.2
rm dist/yams/libwebpmux.so.2
rm dist/yams/libX11.so.6
rm dist/yams/libX11-xcb.so.1
rm dist/yams/libXau.so.6
rm dist/yams/libxcb-glx.so.0
rm dist/yams/libxcb-present.so.0
rm dist/yams/libxcb-render.so.0
rm dist/yams/libxcb-shm.so.0
rm dist/yams/libxcb-sync.so.1
rm dist/yams/libxcb-xfixes.so.0
rm dist/yams/libXcomposite.so.1
rm dist/yams/libXcursor.so.1
rm dist/yams/libXdamage.so.1
rm dist/yams/libXdmcp.so.6
rm dist/yams/libXext.so.6
rm dist/yams/libXfixes.so.3
rm dist/yams/libXft.so.2
rm dist/yams/libXinerama.so.1
rm dist/yams/libXi.so.6
rm dist/yams/libxkbcommon.so.0
rm dist/yams/libXrandr.so.2
rm dist/yams/libXrender.so.1
rm dist/yams/libxshmfence.so.1
rm dist/yams/libXss.so.1
rm dist/yams/libXxf86vm.so.1
rm dist/yams/libz.so.1
rm dist/yams/matplotlib.ttconv.so
rm dist/yams/PIL._imagingft.so
rm dist/yams/PIL._imaging.so
rm dist/yams/PIL._webp.so
rm dist/yams/PyQt5.QtPrintSupport.so
rm dist/yams/PyQt5.Qt.so
rm dist/yams/PyQt5.QtSvg.so
rm dist/yams/PyQt5.QtX11Extras.so
rm dist/yams/resource.so
rm dist/yams/zmq.backend.cython.constants.so
rm dist/yams/zmq.backend.cython.context.so
rm dist/yams/zmq.backend.cython._device.so
rm dist/yams/zmq.backend.cython.error.so
rm dist/yams/zmq.backend.cython.message.so
rm dist/yams/zmq.backend.cython._poll.so
rm dist/yams/zmq.backend.cython.socket.so
rm dist/yams/zmq.backend.cython.utils.so
rm dist/yams/zmq.backend.cython._version.so
tar -zcvf dist/yams-0.1.tar.gz dist/yams
