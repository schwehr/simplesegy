# GNU -*- makefile -*- for emacs
# Created by Kurt Schwehr (kurt@ccom.unh.edu) 26-Jan-2009

VERSION := ${shell cat VERSION}
PKG:=simplesegy
DIST_TAR=dist/${PKG}-${VERSION}.tar.bz2

default:
	@echo
	@echo "  *** Welcome to ${PKG}-py ${VERSION} ***"
	@echo
	@echo "             SEGY Reader"

	@echo "  sdist - Make a tar for release"

sdist:
	./setup.py sdist --formats=bztar
	md5 dist/simplesegy-${VERSION}.tar.bz2

upload:
	scp ${DIST_TAR} vislab-ccom:www/software/${PKG}/downloads/
	scp HISTORY.html vislab-ccom:www/software/${PKG}/

svn-branch:
	svn cp https://cowfish.unh.edu/projects/schwehr/trunk/src/${PKG} https://cowfish.unh.edu/projects/schwehr/branches/${PKG}/${PKG}-${VERSION}

register:
	./setup.py register
