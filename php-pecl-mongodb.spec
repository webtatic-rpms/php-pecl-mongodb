%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}

%global basepkg   %{?basepkg}%{!?basepkg:php}
%global pecl_name mongodb
%global with_zts  0%{?__ztsphp:1}

Name:           %{basepkg}-pecl-mongodb
Version:        1.2.8
Release:        1%{?rcver:.%{rcver}}%{?dist}
Summary:        PECL package MongoDB driver

License:        BSD
Group:          Development/Languages
URL:            http://pecl.php.net/package/mongodb
Source0:        http://pecl.php.net/get/mongodb-%{version}%{?rcver}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  automake %{basepkg}-devel %{basepkg}-pear >= 1:1.4.9-1.2
BuildRequires:  openssl-devel

%if 0%{?fedora}
%define config_flags --with-libedit
BuildRequires:  libedit-devel
%else
%define config_flags --without-libedit
%endif

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Provides:       php-pecl(mongodb) = %{version}

%if 0%{?php_zend_api}
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
%else
Requires:       php-api = %{php_apiver}
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif

%description
The mongodb extension provides exceptionally thin glue between MongoDB
and PHP, implementing only fundemental and performance-critical components
necessary to build a fully-functional MongoDB driver.


%prep
%setup -qc
[ -f package2.xml ] || mv package.xml package2.xml
mv package2.xml %{pecl_name}.xml

%if %{with_zts}
cp -r %{pecl_name}-%{version}%{?rcver} %{pecl_name}-%{version}%{?rcver}-zts
%endif


%build
pushd %{pecl_name}-%{version}%{?rcver}
phpize
%configure --enable-mongodb --with-php-config=%{_bindir}/php-config
CFLAGS="$RPM_OPT_FLAGS" make
popd

%if %{with_zts}
pushd %{pecl_name}-%{version}%{?rcver}-zts
zts-phpize
%configure --enable-mongodb --with-php-config=%{_bindir}/zts-php-config
CFLAGS="$RPM_OPT_FLAGS" make
popd
%endif


%install
rm -rf $RPM_BUILD_ROOT

pushd %{pecl_name}-%{version}%{?rcver}

# install NZTS extension
make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install config file
install -d $RPM_BUILD_ROOT%{php_inidir}
cat > $RPM_BUILD_ROOT%{php_inidir}/%{pecl_name}.ini << 'EOF'
; Enable mongodb extension module
extension=%{pecl_name}.so
EOF

popd

%if %{with_zts}
pushd %{pecl_name}-%{version}%{?rcver}-zts

# install ZTS extension
make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install config file
install -d $RPM_BUILD_ROOT%{php_ztsinidir}
cat > $RPM_BUILD_ROOT%{php_ztsinidir}/%{pecl_name}.ini << 'EOF'
; Enable mongodb extension module
zend_extension=%{php_ztsextdir}/%{pecl_name}.so
EOF

popd
%endif


# Install XML package description
install -d $RPM_BUILD_ROOT%{pecl_xmldir}
install -pm 644 %{pecl_name}.xml $RPM_BUILD_ROOT%{pecl_xmldir}/%{pecl_name}.xml


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc %{pecl_name}-%{version}%{?rcver}/{LICENSE,README.md}
%config(noreplace) %{php_inidir}/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{pecl_name}.xml
%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{pecl_name}.ini
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Sun Apr 23 2017 Andy Thompson <andy@webtatic.com> 1.2.8-1
- update to 1.2.8

* Sat Dec 10 2016 Andy Thompson <andy@webtatic.com> 1.2.1-1
- update to 1.2.1

* Fri Oct 07 2016 Andy Thompson <andy@webtatic.com> 1.1.8-3
- Rebuild for php(API) update

* Sun Aug 21 2016 Andy Thompson <andy@webtatic.com> 1.1.8-1
- Change config to PHP extension

* Sun Aug 21 2016 Andy Thompson <andy@webtatic.com> 1.1.8-1
- Initial spec
