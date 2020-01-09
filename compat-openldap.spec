%global _hardened_build 1

Summary: OpenLDAP compatibility shared libraries
Name: compat-openldap
Epoch: 1
Version: 2.3.43
Release: 5%{?dist}
License: OpenLDAP
Group: System Environment/Libraries
URL: http://www.openldap.org/

Source0: ftp://ftp.OpenLDAP.org/pub/OpenLDAP/openldap-release/openldap-%{version}.tgz

Patch0: openldap-ldaprc.patch
Patch1: openldap-gethostbyXXXX_r.patch
Patch2: openldap-setugid.patch
Patch3: openldap-config-sasl-options.patch
Patch4: openldap-network-timeout.patch
Patch5: openldap-chase-referral.patch
Patch6: openldap-tls-null-char.patch
Patch7: openldap-compat-macros.patch
Patch8: openldap-ai-addrconfig.patch

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires: glibc-devel, cyrus-sasl-devel >= 2.1, openssl-devel
# require current OpenLDAP libraries to have /etc/openldap/ldap.conf
Requires: openldap >= 2.4

%description
OpenLDAP is an open source suite of LDAP (Lightweight Directory Access
Protocol) applications and development tools. The compat-openldap package
includes older versions of the OpenLDAP shared libraries which may be
required by some applications.


%prep
%setup -q -n openldap-%{version}

for patch in %patches; do
	%__patch -p1 -i $patch
done


%build

export CFLAGS="%{optflags} -fPIC -D_GNU_SOURCE -D_REENTRANT -fno-strict-aliasing"

%configure \
	--enable-debug \
	--enable-dynamic \
	--disable-syslog \
	--disable-proctitle \
	--enable-ipv6 \
	--enable-local \
	\
	--disable-slapd \
	--disable-slurpd \
	\
	--disable-modules \
	--disable-backends \
	--disable-overlays \
	\
	--disable-static \
	--enable-shared \
	\
	--with-cyrus-sasl \
	--without-fetch \
	--with-threads \
	--with-tls=openssl \
	--with-gnu-ld \
	--with-pic

# get rid of rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%install
rm -rf %{buildroot}

pushd libraries
	make install DESTDIR=%{buildroot}

	# drop libarchive files
	rm -f %{buildroot}%{_libdir}/*.la

	# two sets of libraries share the soname, compat is not default
	rm -f %{buildroot}/%{_libdir}/*.so

	# fix permissions to correctly generate debuginfo
	chmod 0755 %{buildroot}/%{_libdir}/*
popd

# remove all configuration files
rm -rf %{buildroot}/etc


%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc ANNOUNCEMENT
%doc COPYRIGHT
%doc LICENSE
%attr(0755,root,root) %{_libdir}/liblber-2.3.so.*
%attr(0755,root,root) %{_libdir}/libldap-2.3.so.*
%attr(0755,root,root) %{_libdir}/libldap_r-2.3.so.*


%changelog
* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1:2.3.43-5
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1:2.3.43-4
- Mass rebuild 2013-12-27

* Tue May 07 2013 Jan Synáček <jsynacek@redhat.com> - 1:2.3.43-3.2
- Remove undefined rpm macros (#960090)

* Fri Apr 19 2013 Daniel Mach <dmach@redhat.com> - 1:2.3.43-3.1
- Rebuild for cyrus-sasl

* Wed Aug 15 2012 Jan Vcelak <jvcelak@redhat.com> 1:2.3.43-3
- enhancement: build with hardening flags (RELRO)
- fix: querying for IPv6 DNS records when IPv6 is disabled on the host (#835013)
- drop unnecessary patches
- clean configure flags

* Mon Nov 22 2010 Jan Vcelak <jvcelak@redhat.com> 1:2.3.43-2
- run ldconfig in post and postun
- remove rpath

* Thu Nov 11 2010 Jan Vcelak <jvcelak@redhat.com> 1:2.3.43-1
- split from openldap package
