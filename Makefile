PREFIX=/usr
BINDIR=${PREFIX}/bin
ICODIR=${PREFIX}/share/icons/hicolor/256x256/apps
APPDIR=${PREFIX}/share/applications

install:
	install -Dv xsft.py ${BINDIR}
	install -Dv xsft.png ${ICODIR}
	install -Dv xrandr-slightly-fewer-tears.desktop ${APPDIR}

uninstall:
	rm -f ${BINDIR}/xsft.py
	rm -f ${ICODIR}/xsfticon.png
	rm -f ${APPDIR}/xrandr-slightly-fewer-tears.desktop
