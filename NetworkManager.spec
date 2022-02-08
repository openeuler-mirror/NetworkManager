%global dbus_glib_version 0.100
%global wireless_tools_version 1:28-0pre9
%global wpa_supplicant_version 1:1.1
%global ppp_version %(sed -n 's/^#define\\s*VERSION\\s*"\\([^\\s]*\\)"$/\\1/p' %{_includedir}/pppd/patchlevel.h 2>/dev/null | grep . || echo bad)
%global glib2_version %(pkg-config --modversion glib-2.0 2>/dev/null || echo bad)
%global real_version 1.26.2
%global snapshot %{nil}
%global git_sha %{nil}
%global obsoletes_device_plugins 1:0.9.9.95-1
%global obsoletes_ppp_plugin     1:1.5.3
%global systemd_dir %{_prefix}/lib/systemd/system

%if "x%{?snapshot}" != x
%global snapshot_dot .%{snapshot}
%endif
%if "x%{?git_sha}" != x
%global git_sha_dot .%{git_sha}
%endif

%global snap %{?snapshot_dot}%{?git_sha_dot}
%global real_version_major %(printf '%s' '%{real_version}' | sed -n 's/^\\([1-9][0-9]*\\.[1-9][0-9]*\\)\\.[1-9][0-9]*$/\\1/p')

%bcond_with    python2
%bcond_without adsl
%bcond_without bluetooth
%bcond_without wwan
%bcond_without team
%bcond_without wifi
%bcond_with iwd
%bcond_without ovs
%bcond_without ppp
%bcond_without nmtui
%bcond_without regen_docs
%bcond_with    debug
%bcond_with    test
%bcond_with    lto
%bcond_with    sanitizer
%bcond_with libnm_glib
%bcond_without crypto_gnutls
%bcond_without nm_cloud_setup
%bcond_with    firewalld_zone

%global dbus_version 1.1
%global dbus_sys_dir %{_sysconfdir}/dbus-1/system.d
%global with_modem_manager_1 1
%global dhcp_default dhclient

Name:             NetworkManager
Version:          1.26.2
Epoch:            1
Release:          12
Summary:          Network Link Manager and User Applications
License:          GPLv2+
URL:              https://www.gnome.org/projects/NetworkManager/
Source:           https://download.gnome.org/sources/NetworkManager/%{real_version_major}/%{name}-%{version}.tar.xz
Source1:          NetworkManager.conf
Source2:          00-server.conf
# PATCH-FEATURE-FIX fix-wants-and-add-requires.patch --fix wants and add requires in the file of NetworkManager.service.in
Patch1:        fix-wants-and-add-requires.patch
Patch2:        bugfix-NetworkManager-restarting-service-on-dependency-failure.patch
Patch3:        backport-device-fix-wrongly-considering-ipv6-may-fail-for-ipv4.patch
Patch4:        backport-bugfix-nmcli-field-active-show-error.patch
Patch5:        backport-amend-edit-translation-of-nmcli.patch
Patch6:        backport-core-fix-crash-in-nm_wildcard_match_check.patch
Patch7:        backport-core-ovs-fix-leak-of-NMOvsdbPrivate-db_uuid.patch
Patch8:        backport-libnm-fix-leak-and-return-failures-from-nm-client-load-connections.patch

BuildRequires:    gcc libtool pkgconfig automake autoconf intltool gettext-devel ppp-devel gnutls-devel
BuildRequires:    dbus-devel dbus-glib-devel  glib2-devel gobject-introspection-devel jansson-devel
BuildRequires:    dhclient readline-devel audit-libs-devel gtk-doc libudev-devel libuuid-devel /usr/bin/valac polkit-devel
BuildRequires:    iptables libxslt bluez-libs-devel systemd systemd-devel libcurl-devel libndp-devel python3-gobject-base teamd-devel
BuildRequires:    ModemManager-glib-devel newt-devel /usr/bin/dbus-launch python3 python3-dbus libselinux-devel chrpath
%if %{with python2}
BuildRequires:    python2 pygobject3-base python2-dbus
%endif

%if %{with firewalld_zone}
BuildRequires:    firewalld-filesystem
%endif

Requires(post):   systemd
Requires(post):   /usr/sbin/update-alternatives
Requires(preun):  systemd
Requires(preun):  /usr/sbin/update-alternatives
Requires(postun): systemd
Requires:         dbus  glib2 wpa_supplicant  bluez
Requires:         %{name}-libnm = %{epoch}:%{version}-%{release} %{name}-help
Obsoletes:        NetworkManager < %{obsoletes_device_plugins} NetworkManager < %{obsoletes_ppp_plugin}
Obsoletes:        dhcdbd NetworkManager < 1.0.0
Obsoletes:        NetworkManager-wimax < 1.2
Obsoletes:        NetworkManager-bt NetworkManager-atm
Conflicts:        NetworkManager-vpnc < 1:0.7.0.99-1 NetworkManager-openvpn < 1:0.7.0.99-1
Conflicts:        NetworkManager-pptp < 1:0.7.0.99-1 NetworkManager-openconnect < 0:0.7.0.99-1
Conflicts:        kde-plasma-networkmanagement < 1:0.9-0.49.20110527git.nm09

Provides:         %{name}-dispatcher-routing-rules
Obsoletes:        %{name}-dispatcher-routing-rules
Provides:         %{name}-config-routing-rules = %{epoch}:%{version}-%{release}
Obsoletes:        %{name}-config-routing-rules < %{epoch}:%{version}-%{release}
Provides:         %{name}-ppp
Obsoletes:        %{name}-ppp
Provides:         %{name}-wifi
Obsoletes:        %{name}-wifi
Provides:         %{name}-team
Obsoletes:        %{name}-team
Provides:         %{name}-ovs
Obsoletes:        %{name}-ovs
Provides:         %{name}-bluetooth
Obsoletes:        %{name}-bluetooth
Provides:         %{name}-tui
Obsoletes:        %{name}-tui
Provides:         %{name}-adsl
Obsoletes:        %{name}-adsl

%description
NetworkManager attempts to keep an active network connection available
at all times.  The point of NetworkManager is to make networking
configuration and setup as painless and automatic as possible.	If
using DHCP, NetworkManager is intended to replace default routes,
obtain IP addresses from a DHCP server, and change name servers
whenever it sees fit.

%package          wwan
Summary:          Mobile broadband device plugin for %{name}
Requires:         %{name} = %{epoch}:%{version}-%{release}
Requires:         ModemManager
Obsoletes:        NetworkManager < %{obsoletes_device_plugins}

%description      wwan
This package contains NetworkManager support for mobile broadband (WWAN)
devices.

%package          libnm
Summary:          Libraries for adding NetworkManager support to applications (new API).
Conflicts:        NetworkManager-glib < %{epoch}:%{version}-%{release}

%description      libnm
This package contains the libraries that add NetworkManager support to applications (new API).

%package          libnm-devel
Summary:          Header files and Development files for adding NetworkManager support to applications (new API).
Requires:         %{name}-libnm = %{epoch}:%{version}-%{release} pkgconfig glib2-devel

%description      libnm-devel
This package contains the header and development files  for
developing applications that use %{name}-libnm.

%package          config-server
Summary:          NetworkManager config file for "server-like" defaults
BuildArch:        noarch

%description      config-server
This adds a NetworkManager configuration file to make it behave more
like the old "network" service. In particular, it stops NetworkManager
from automatically running DHCP on unconfigured ethernet devices, and
allows connections with static IP addresses to be brought up even on
ethernet devices with no carrier.

%package_help

%prep
%autosetup -p1 -n NetworkManager-%{version}

%build
%if %{with regen_docs}
gtkdocize
%endif
autoreconf --install --force
intltoolize --automake --copy --force
%configure \
	--disable-silent-rules \
	--with-dhclient=yes \
	--with-dhcpcd=no \
	--with-dhcpcanon=no \
	--with-config-dhcp-default=%{dhcp_default} \
%if %{with crypto_gnutls}
	--with-crypto=gnutls \
%else
	--with-crypto=nss \
%endif
%if %{with sanitizer}
	--with-address-sanitizer=exec \
%else
	--with-address-sanitizer=no \
	--disable-undefined-sanitizer \
%endif
%if %{with debug}
	--enable-more-logging \
	--with-more-asserts=10000 \
%else
	--disable-more-logging \
	--without-more-asserts \
%endif
	--enable-ld-gc \
%if %{with lto}
	--enable-lto \
%else
	--disable-lto \
%endif
	--with-libaudit=yes-disabled-by-default \
%if 0%{?with_modem_manager_1}
	--with-modem-manager-1=yes \
%else
	--with-modem-manager-1=no \
%endif
%if %{with wifi}
	--enable-wifi=yes \
	--with-wext=no \
%else
	--enable-wifi=no \
%endif
%if %{with iwd}
	--with-iwd=yes \
%else
	--with-iwd=no \
%endif
	--enable-vala=yes \
	--enable-introspection \
%if %{with regen_docs}
	--enable-gtk-doc \
%else
	--disable-gtk-doc \
%endif
%if %{with team}
	--enable-teamdctl=yes \
%else
	--enable-teamdctl=no \
%endif
%if %{with ovs}
	--enable-ovs=yes \
%else
	--enable-ovs=no \
%endif
	--with-selinux=yes \
	--enable-polkit=yes \
	--enable-polkit-agent \
	--enable-modify-system=yes \
	--enable-concheck \
	--without-libpsl \
	--without-ebpf \
	--with-session-tracking=systemd \
	--with-suspend-resume=systemd \
	--with-systemdsystemunitdir=%{systemd_dir} \
	--with-system-ca-path=/etc/pki/tls/cert.pem \
	--with-dbus-sys-dir=%{dbus_sys_dir} \
	--with-tests=yes \
%if %{with test}
	--enable-more-warnings=error \
%else
	--enable-more-warnings=yes \
%endif
	--with-valgrind=no \
	--enable-ifcfg-rh=yes \
%if %{with ppp}
	--with-pppd-plugin-dir=%{_libdir}/pppd/%{ppp_version} \
	--enable-ppp=yes \
%endif
%if %{with firewalld_zone}
	--enable-firewalld-zone \
%else
	--disable-firewalld-zone \
%endif
	--with-dist-version=%{version}-%{release} \
	--with-config-plugins-default='ifcfg-rh' \
	--with-config-dns-rc-manager-default=symlink \
	--with-config-logging-backend-default=journal \
	--enable-json-validation \
%if %{with libnm_glib}
	--with-libnm-glib \
%else
	--without-libnm-glib \
%endif
%if %{with nm_cloud_setup}
	--with-nm-cloud_setup=yes
%else
	--with-nm-cloud_setup=no
%endif

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
cp  %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/
cp  %{SOURCE2} %{buildroot}%{_prefix}/lib/%{name}/conf.d/
cp examples/dispatcher/10-ifcfg-rh-routes.sh %{buildroot}%{_sysconfdir}/%{name}/dispatcher.d/
ln -s ../no-wait.d/10-ifcfg-rh-routes.sh %{buildroot}%{_sysconfdir}/%{name}/dispatcher.d/pre-up.d/
ln -s ../10-ifcfg-rh-routes.sh %{buildroot}%{_sysconfdir}/%{name}/dispatcher.d/no-wait.d/

%find_lang %{name}
chrpath -d %{buildroot}/%{_libdir}/%{name}/%{version}-%{release}/*.so*
mkdir -p %{buildroot}/etc/ld.so.conf.d
echo "%{_libdir}/%{name}/%{version}-%{release}" > %{buildroot}/etc/ld.so.conf.d/%{name}-%{_arch}.conf

%delete_la_and_a
find %{buildroot}%{_datadir}/gtk-doc -exec touch --reference configure.ac '{}' \+
%if 0%{?__debug_package}
mkdir -p %{buildroot}%{_prefix}/src/debug/NetworkManager-%{real_version}
cp valgrind.suppressions %{buildroot}%{_prefix}/src/debug/NetworkManager-%{real_version}
%endif

touch %{buildroot}%{_sbindir}/ifup %{buildroot}%{_sbindir}/ifdown

%check
make %{?_smp_mflags} check

%pre
if [ -f "%{systemd_dir}/network-online.target.wants/NetworkManager-wait-online.service" ] ; then
        systemctl enable NetworkManager-wait-online.service || :
	fi

%post
/usr/bin/udevadm control --reload-rules || :
/usr/bin/udevadm trigger --subsystem-match=net || :
%systemd_post NetworkManager.service NetworkManager-wait-online.service NetworkManager-dispatcher.service
%triggerin -- initscripts
if [ -f %{_sbindir}/ifup -a ! -L %{_sbindir}/ifup ]; then
    /usr/sbin/update-alternatives --remove ifup %{_libexecdir}/nm-ifup >/dev/null 2>&1 || :
else
   /usr/sbin/update-alternatives --install %{_sbindir}/ifup ifup %{_libexecdir}/nm-ifup 50 \
        --slave %{_sbindir}/ifdown ifdown %{_libexecdir}/nm-ifdown
fi
/sbin/ldconfig

%preun
if [ $1 -eq 0 ]; then
    /bin/systemctl --no-reload disable NetworkManager.service >/dev/null 2>&1 || :
    /usr/sbin/update-alternatives --remove ifup %{_libexecdir}/nm-ifup >/dev/null 2>&1 || :
fi
%systemd_preun NetworkManager-wait-online.service NetworkManager-dispatcher.service

%postun
/usr/bin/udevadm control --reload-rules || :
/usr/bin/udevadm trigger --subsystem-match=net || :

%if %{with firewalld_zone}
%firewalld_reload
%endif

%systemd_postun NetworkManager.service NetworkManager-wait-online.service NetworkManager-dispatcher.service

%ldconfig_scriptlets glib
%ldconfig_scriptlets libnm
/sbin/ldconfig

%files
%defattr(-,root,root)
%doc AUTHORS 
%license COPYING
%{_datadir}/doc/NetworkManager/examples/server.conf
%{_bindir}/nmcli
%{_bindir}/nm-online
%{_sbindir}/NetworkManager
%exclude %{_libexecdir}/nm-initrd-generator
%ghost %attr(755, root, root) %{_sbindir}/ifdown
%ghost %attr(755, root, root) %{_sbindir}/ifup
%dir %{_prefix}/lib/NetworkManager/conf.d
%dir %{_prefix}/lib/NetworkManager/VPN
%{systemd_dir}/NetworkManager.service
%{systemd_dir}/NetworkManager-wait-online.service
%{systemd_dir}/NetworkManager-dispatcher.service
%{_prefix}/lib/udev/rules.d/*.rules
%{_libdir}/%{name}/%{version}-%{release}/*.so
%{_libexecdir}/nm-if*
%{_libexecdir}/nm-dhcp-helper
%{_libexecdir}/nm-dispatcher
%{_datadir}/bash-completion/completions/nmcli
%{dbus_sys_dir}/*.conf
%{_datadir}/dbus-1/system-services/*.service
%{_datadir}/polkit-1/actions/*.policy
%dir %{_sysconfdir}/NetworkManager/conf.d
%dir %{_sysconfdir}/NetworkManager/dispatcher.d/pre-down.d
%dir %{_sysconfdir}/NetworkManager/dnsmasq.d
%dir %{_sysconfdir}/NetworkManager/dnsmasq-shared.d
%dir %{_sysconfdir}/NetworkManager/system-connections
%dir %{_sysconfdir}/sysconfig/network-scripts
%{_sysconfdir}/NetworkManager/NetworkManager.conf
%dir %{_localstatedir}/lib/%{name}
%{_sysconfdir}/%{name}/dispatcher.d/10-ifcfg-rh-routes.sh
%{_sysconfdir}/%{name}/dispatcher.d/no-wait.d/10-ifcfg-rh-routes.sh
%{_sysconfdir}/%{name}/dispatcher.d/pre-up.d/10-ifcfg-rh-routes.sh
%{_libdir}/pppd/%{ppp_version}/nm-pppd-plugin.so
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-wifi.so
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-team.so
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-ovs.so
%{systemd_dir}/NetworkManager.service.d/NetworkManager-ovs.conf
%{_libdir}/%{name}/%{version}-%{release}/libnm-ppp-plugin.so
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-bluetooth.so
%{_bindir}/nmtui*
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-adsl.so
%if %{with nm_cloud_setup}
%{_libexecdir}/nm-cloud-setup
%{systemd_dir}/nm-cloud-setup.service
%{systemd_dir}/nm-cloud-setup.timer
%{_prefix}/lib/%{name}/dispatcher.d/90-nm-cloud-setup.sh
%{_prefix}/lib/%{name}/dispatcher.d/no-wait.d/90-nm-cloud-setup.sh
%endif
%if %{with firewalld_zone}
%{_prefix}/lib/firewalld/zones/nm-shared.xml
%endif
%config(noreplace) /etc/ld.so.conf.d/*

%files wwan
%defattr(-,root,root)
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-wwan.so
%{_libdir}/%{name}/%{version}-%{release}/libnm-wwan.so

%files libnm -f %{name}.lang
%defattr(-,root,root)
%{_libdir}/libnm.so.0*
%{_libdir}/girepository-1.0/*.typelib

%files libnm-devel
%defattr(-,root,root)
%{_includedir}/libnm/*.h
%{_libdir}/pkgconfig/*.pc
%{_libdir}/libnm.so
%{_datadir}/gir-1.0/NM-1.0.gir
%{_datadir}/vala/vapi/libnm*
%{_datadir}/dbus-1/interfaces/*.xml

%files config-server
%{_prefix}/lib/%{name}/conf.d/00-server.conf

%files help
%defattr(-,root,root)
%doc CONTRIBUTING NEWS README TODO
%{_mandir}/man1/nmcli.1.gz
%{_mandir}/man1/nm-online.1.gz
%{_mandir}/man5/*.5.gz
%{_mandir}/man7/nmcli-examples.7.gz
%{_mandir}/man8/*.8.gz
%{_mandir}/man7/nm-openvswitch.7.gz
%{_mandir}/man1/nmtui*.1.gz
%{_datadir}/gtk-doc/html/libnm/*
%{_datadir}/gtk-doc/html/NetworkManager/*

%changelog
* Mon Feb 7 2022 seuzw <930zhaowei@163.com> - 1.26.2-12
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:libnm: fix leak and return failures from nm_client_load_connections()

* Sat Jan 22 2022 seuzw <930zhaowei@163.com> - 1.26.2-11
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:backport patches to fix crash in nm_wildcard_match_check and fix leak of NMOvsdbPrivate.db_uuid

* Thu Sep 23 2021 gaoxingwang <gaoxingwang@huawei.com> - 1.26.2-10
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:remove rpath

* Thu Aug 5 2021 gaoxingwang <gaoxingwang@huawei.com> - 1.26.2-9
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:amend edit translation of nmcli

* Wed Aug 4 2021 gaoxingwang <gaoxingwang@huawei.com> - 1.26.2-8
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix 'nmcli -f NAME,ACTIVE',active column display error

* Tue Aug 3 2021 gaoxingwang <gaoxingwang@huawei.com> - 1.26.2-7
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:sync from upstream, fix wrongly considering ipv6.may-fail for ipv4

* Fri Jul 30 2021 jiazhenyuan <jiazhenyuan@uniontech.com> - 1.26.2-6
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix dbus-daemon error when systemd-resolved service was not enabled

* Fri Mar 12 2021 yanan <yanan@huawei.com> - 1.26.2-5
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:use multi thread to build

* Thu Dec 10 2020 yuboyun <yuboyun@huawei.com> - 1.26.2-4
- Type:bugfix
- CVE:NA
- SUG:NA
- DESC:add macro firewalld_zone to fix firewalld error about nm-shared.xml

* Thu Dec 10 2020 yuboyun <yuboyun@huawei.com> - 1.26.2-3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix NetworkManager restarting service on dependency failure

* Mon Nov 09 2020 xihaochen <xihaochen@huawei.com> - 1.26.2-2
- Type:requirement
- CVE:NA
- SUG:NA
- DESC:add NetworkManager-help dependency for Networkmanager

* Thu Aug 27 2020 yuboyun <yuboyun@huawei.com> - 1.26.2-1
- update to 1.26.2

* Thu Feb 27 2020 openEuler Buildteam <buildteam@openeuler.org> - 1.16.0-7
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix build require of GObject introspection for python

* Mon Dec 23 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.16.0-6
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:modify the patches

* Mon Oct 28 2019 caomeng <caomeng5@huawei.com> - 1.16.0-5
- Type:NA
- ID:NA
- SUG:NA
- DESC:add systemd_postun para

* Fri Sep 27 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.16.0-4
- Type:bugfix
- ID:NA
- SUG:NA
  DESC:the Sub-package of config-server fallback

* Thu Sep 26 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.16.0-3
- Type:bugfix
- ID:NA
- SUG:NA
  DESC:version fallback

* Wed Sep 25 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.16.0-2
- Type:bugfix
- ID:NA
- SUG:NA
  DESC:bugfix nmtui problem team module

* Sat Sep 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.16.0-1
- Package init

