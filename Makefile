MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
CUR_DIR := $(patsubst %/,%,$(dir $(MKFILE_PATH)))
CUR_NAME := $(notdir $(CUR_DIR))

mock        := /usr/bin/mock


clean:
	rm -rf target
	$(mock) --clean

rpm:
	mkdir -p target/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	cp -t target/rpmbuild/SOURCES *.service *.sh
	rpmbuild -ba --define '_topdir $(CUR_DIR)/target/rpmbuild' $(CUR_NAME).spec

#rpm-mock:
#	$(eval SOURCE_RPM_FILE :=$(shell rpmbuild --define '_topdir $(CUR_DIR)/target/rpmbuild' -bs $(CUR_NAME).spec | sed -e 's/Wrote: //'))
#	$(eval MOCK_ROOT       :=$(shell /usr/bin/mock -p))
#	$(eval ARCHITECTURE    :=$(shell uname -m))
#	$(mock) --installdeps --rebuild $(SOURCE_RPM_FILE)
#	mkdir -p target/rpmbuild/RPMS/$(ARCHITECTURE)/
#	cp $(MOCK_ROOT)../result/*.$(ARCHITECTURE).rpm target/rpmbuild/RPMS/$(ARCHITECTURE)/
#	cp $(MOCK_ROOT)../result/*.src.rpm target/rpmbuild/SRPMS/
#	cp $(MOCK_ROOT)../result/build.log target/result
	

#rpm-sign:
#	(\
#	  echo set timeout -1;\
#	  echo spawn rpmsign --addsign target/rpmbuild/RPMS/*/*.rpm;\
#	  echo expect -exact \"Enter pass phrase:\";\
#	  echo send -- \"$(GPG_PASSPHRASE)\\r\";\
#	  echo expect eof;\
#	) | expect

.PHONY: clean rpm
.DEFAULT_GOAL := rpm
