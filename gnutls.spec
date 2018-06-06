%bcond_without dane
%if 0%{?rhel}
%bcond_with guile
%bcond_with fips
%else
%bcond_without guile
%bcond_with fips
%endif

Summary: A TLS protocol implementation
Name: gnutls
Version: 3.5.7
Release: 3%{?dist}
# The libraries are LGPLv2.1+, utilities are GPLv3+
License: GPLv3+ and LGPLv2+
Group: System Environment/Libraries
BuildRequires: p11-kit-devel >= 0.21.3, gettext-devel
BuildRequires: zlib-devel, readline-devel, libtasn1-devel >= 4.3
BuildRequires: libtool, automake, autoconf, texinfo
BuildRequires: autogen-libopts-devel >= 5.18 autogen
BuildRequires: nettle-devel >= 3.1.1
BuildRequires: trousers-devel >= 0.3.11.2
BuildRequires: libidn2-devel
BuildRequires: libunistring-devel
BuildRequires: gperf, net-tools, datefudge, softhsm
%if %{with fips}
BuildRequires: fipscheck
%endif

# for a sanity check on cert loading
BuildRequires: p11-kit-trust, ca-certificates
Requires: crypto-policies
Requires: p11-kit-trust
Requires: libtasn1 >= 4.3
Recommends: trousers >= 0.3.11.2

%if %{with dane}
BuildRequires: unbound-devel unbound-libs
%endif
%if %{with guile}
BuildRequires: guile-devel
%endif
URL: http://www.gnutls.org/
Source0: ftp://ftp.gnutls.org/gcrypt/gnutls/%{name}-%{version}.tar.xz
Source1: ftp://ftp.gnutls.org/gcrypt/gnutls/%{name}-%{version}.tar.xz.sig
Source2: gpgkey-1F42418905D8206AA754CCDC29EE58B996865171.gpg

# Wildcard bundling exception https://fedorahosted.org/fpc/ticket/174
Provides: bundled(gnulib) = 20130424

%package c++
Summary: The C++ interface to GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}

%package devel
Summary: Development files for the %{name} package
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{name}-c++%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%endif
Requires: pkgconfig
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%package utils
License: GPLv3+
Summary: Command line tools for TLS protocol
Group: Applications/System
Requires: %{name}%{?_isa} = %{version}-%{release}
%if %{with dane}
Requires: %{name}-dane%{?_isa} = %{version}-%{release}
%endif

%if %{with dane}
%package dane
Summary: A DANE protocol implementation for GnuTLS
Requires: %{name}%{?_isa} = %{version}-%{release}
%endif

%if %{with guile}
%package guile
Summary: Guile bindings for the GNUTLS library
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: guile
%endif

%description
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 

%description c++
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 

%description devel
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 
This package contains files needed for developing applications with
the GnuTLS library.

%description utils
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 
This package contains command line TLS client and server and certificate
manipulation tools.

%if %{with dane}
%description dane
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 
This package contains library that implements the DANE protocol for verifying
TLS certificates through DNSSEC.
%endif

%if %{with guile}
%description guile
GnuTLS is a secure communications library implementing the SSL, TLS and DTLS 
protocols and technologies around them. It provides a simple C language 
application programming interface (API) to access the secure communications 
protocols as well as APIs to parse and write X.509, PKCS #12, OpenPGP and 
other required structures. 
This package contains Guile bindings for the library.
%endif

%prep
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}

%setup -q

sed -i -e 's|sys_lib_dlsearch_path_spec="/lib /usr/lib|sys_lib_dlsearch_path_spec="/lib /usr/lib %{_libdir}|g' configure
rm -f lib/minitasn1/*.c lib/minitasn1/*.h
rm -f src/libopts/*.c src/libopts/*.h src/libopts/compat/*.c src/libopts/compat/*.h 

echo "SYSTEM=NORMAL" >> tests/system.prio

%build
%configure --with-libtasn1-prefix=%{_prefix} \
%if %{with fips}
           --enable-fips140-mode \
%endif
           --disable-static \
           --disable-openssl-compatibility \
           --disable-non-suiteb-curves \
           --with-system-priority-file=%{_sysconfdir}/crypto-policies/back-ends/gnutls.config \
           --with-default-trust-store-pkcs11="pkcs11:" \
           --with-trousers-lib=%{_libdir}/libtspi.so.1 \
           --htmldir=%{_docdir}/manual \
%if %{with guile}
           --enable-guile \
%else
           --disable-guile \
%endif
%if %{with dane}
           --with-unbound-root-key-file=/var/lib/unbound/root.key \
           --enable-dane \
%else
           --disable-dane \
%endif
           --disable-rpath \
           --with-default-priority-string="@SYSTEM"

make %{?_smp_mflags} V=1

%if %{with fips}
%define __spec_install_post \
	%{?__debug_package:%{__debug_install_post}} \
	%{__arch_install_post} \
	%{__os_install_post} \
	fipshmac -d $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_libdir}/libgnutls.so.28.*.* \
	file=`basename $RPM_BUILD_ROOT%{_libdir}/libgnutls.so.28.*.hmac` && mv $RPM_BUILD_ROOT%{_libdir}/$file $RPM_BUILD_ROOT%{_libdir}/.$file && ln -s .$file $RPM_BUILD_ROOT%{_libdir}/.libgnutls.so.28.hmac \
%{nil}
%endif

%install
make install DESTDIR=$RPM_BUILD_ROOT
make -C doc install-html DESTDIR=$RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/guile/2.0/guile-gnutls*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/guile/2.0/guile-gnutls*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/gnutls/libpkcs11mock1.*
%if %{without dane}
rm -f $RPM_BUILD_ROOT%{_libdir}/pkgconfig/gnutls-dane.pc
%endif

%find_lang gnutls

%check
make check %{?_smp_mflags}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post c++ -p /sbin/ldconfig

%postun c++ -p /sbin/ldconfig

%post devel
if [ -f %{_infodir}/gnutls.info.gz ]; then
    /sbin/install-info %{_infodir}/gnutls.info.gz %{_infodir}/dir || :
fi

%preun devel
if [ $1 = 0 -a -f %{_infodir}/gnutls.info.gz ]; then
   /sbin/install-info --delete %{_infodir}/gnutls.info.gz %{_infodir}/dir || :
fi

%if %{with dane}
%post dane -p /sbin/ldconfig

%postun dane -p /sbin/ldconfig
%endif

%if %{with guile}
%post guile -p /sbin/ldconfig

%postun guile -p /sbin/ldconfig
%endif

%files -f gnutls.lang
%defattr(-,root,root,-)
%{_libdir}/libgnutls.so.30*
%if %{with fips}
%{_libdir}/.libgnutls.so.30*.hmac
%endif
%doc README.md AUTHORS NEWS THANKS
%license LICENSE doc/COPYING doc/COPYING.LESSER

%files c++
%{_libdir}/libgnutlsxx.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/libgnutls*.so
%if %{with fips}
%{_libdir}/.libgnutls.so.*.hmac
%endif

%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*
%{_infodir}/gnutls*
%{_infodir}/pkcs11-vision*
%{_docdir}/manual/*

%files utils
%defattr(-,root,root,-)
%{_bindir}/certtool
%{_bindir}/tpmtool
%{_bindir}/ocsptool
%{_bindir}/psktool
%{_bindir}/p11tool
%{_bindir}/srptool
%if %{with dane}
%{_bindir}/danetool
%endif
%{_bindir}/gnutls*
%{_mandir}/man1/*
%doc doc/certtool.cfg

%if %{with dane}
%files dane
%defattr(-,root,root,-)
%{_libdir}/libgnutls-dane.so.*
%endif

%if %{with guile}
%files guile
%defattr(-,root,root,-)
%{_libdir}/guile/2.0/guile-gnutls*.so*
%{_libdir}/guile/2.0/site-ccache/gnutls.go
%{_libdir}/guile/2.0/site-ccache/gnutls/extra.go
%{_datadir}/guile/site/2.0/gnutls.scm
%{_datadir}/guile/site/2.0/gnutls/extra.scm
%endif

%changelog
