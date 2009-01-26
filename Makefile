# GNU -*- makefile -*- for emacs
# Created by Kurt Schwehr (kurt@ccom.unh.edu) 26-Jan-2009

VERSION := ${shell cat VERSION}
PKG:=simplesegy

default:
	@echo
	@echo "  *** Welcome to ${PKG}-py ${VERSION} ***"
	@echo
	@echo "             SEGY Reader"

	@echo "  sdist - Make a tar for release"

sdist:
	./setup.py sdist --formats=bztar
