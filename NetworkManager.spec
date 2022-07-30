%global dbus_glib_version 0.100
%global wireless_tools_version 1:28-0pre9
%global wpa_supplicant_version 1:1.1
%global ppp_version %(sed -n 's/^#define\\s*VERSION\\s*"\\([^\\s]*\\)"$/\\1/p' %{_includedir}/pppd/patchlevel.h 2>/dev/null | grep . || echo bad)
%global glib2_version %(pkg-config --modversion glib-2.0 2>/dev/null || echo bad)
%global real_version 1.32.12
%global snapshot %{nil}
%global git_sha %{nil}
%global obsoletes_device_plugins 1:0.9.9.95-1
%global obsoletes_ppp_plugin     1:1.5.3
%global systemd_dir %{_prefix}/lib/systemd/system

%if "x%{?snapshot}" != "x"
%global snapshot_dot .%{snapshot}
%endif
%if "x%{?git_sha}" != "x"
%global git_sha_dot .%{git_sha}
%endif

%global snap %{?snapshot_dot}%{?git_sha_dot}
%global real_version_major %(printf '%s' '%{real_version}' | sed -n 's/^\\([1-9][0-9]*\\.[1-9][0-9]*\\)\\.[0-9][0-9]*$/\\1/p')

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

%global dbus_version 1.1
%global dbus_sys_dir %{_datadir}/dbus-1/system.d
%if %{with bluetooth} || %{with wwan}
%global with_modem_manager_1 1
%else
%global with_modem_manager_1 0
%endif
%global dhcp_default dhclient

Name:             NetworkManager
Version:          1.32.12
Epoch:            1
Release:          10
Summary:          Network Link Manager and User Applications
License:          GPLv2+
URL:              https://www.gnome.org/projects/NetworkManager/
Source:           https://download.gnome.org/sources/NetworkManager/%{real_version_major}/%{name}-%{version}.tar.xz
Source1:          NetworkManager.conf
Source2:          00-server.conf
Patch1:           fix-wants-and-add-requires.patch
Patch2:           bugfix-use-PartOf-replace-Requires-in-service.patch
Patch3:           bugfix-ipv6-external-route-miss.patch
Patch4:           bugfix-recover-to-30s-timeout-in-NetworkManager-wait-online.patch

Patch6000:        backport-libnm-fix-crash-in-_nm_ip_route_validate_all-for-invalid-route.patch
Patch6001:        backport-libnm-fix-crash-on-failure-of-nm_vpn_plugin_info_new_from_file.patch
Patch6002:        backport-core-reload-config-for-active-devices.patch
Patch6003:        backport-libnm-fix-warning-when-setting-wrong-ethtool-ternary-value.patch

BuildRequires:    gcc libtool pkgconfig automake autoconf intltool gettext-devel ppp-devel gnutls-devel
BuildRequires:    dbus-devel dbus-glib-devel  glib2-devel gobject-introspection-devel jansson-devel
BuildRequires:    dhclient readline-devel audit-libs-devel gtk-doc libudev-devel libuuid-devel /usr/bin/valac polkit-devel
BuildRequires:    iptables libxslt systemd systemd-devel libcurl-devel libndp-devel python3-gobject-base teamd-devel
BuildRequires:    ModemManager-glib-devel newt-devel /usr/bin/dbus-launch python3 python3-dbus libselinux-devel chrpath

%if %{with bluetooth}
BuildRequires:    bluez-libs-devel
%endif
Requires(post):   systemd
Requires(post):   /usr/sbin/update-alternatives
Requires(preun):  systemd
Requires(preun):  /usr/sbin/update-alternatives
Requires(postun): systemd
Requires:         dbus  glib2
Requires:         %{name}-libnm = %{epoch}:%{version}-%{release}
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
Provides:         %{name}-team
Obsoletes:        %{name}-team
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

	
%if %{with wifi}
%package wifi
Summary:          Wifi plugin for NetworkManager
Requires:         %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires:         wpa_supplicant

Obsoletes: NetworkManager < %{obsoletes_device_plugins}

%description wifi
This package contains NetworkManager support for Wifi devices.
%endif

%package          wwan
Summary:          Mobile broadband device plugin for %{name}
Requires:         %{name} = %{epoch}:%{version}-%{release}
Requires:         ModemManager
Obsoletes:        NetworkManager < %{obsoletes_device_plugins}

%description      wwan
This package contains NetworkManager support for mobile broadband (WWAN)
devices.

%if %{with bluetooth}
%package          bluetooth
Summary:          Bluetooth device plugin for %{name}
Requires:         %{name} = %{epoch}:%{version}-%{release}
Requires:         NetworkManager-wwan
Requires:         bluez
Obsoletes:        NetworkManager < %{obsoletes_device_plugins}

%description      bluetooth
This package contains NetworkManager support for Bluetooth device
%endif

%if %{with ovs}
%package ovs
Summary:         Open vSwitch device plugin for NetworkManager
Requires:        %{name} = %{epoch}:%{version}-%{release}
 
%description ovs
This package contains NetworkManager support for Open vSwitch bridges.
%endif

	
%if %{with ppp}
%package ppp
Summary:         PPP plugin for NetworkManager
Requires:        %{name} = %{epoch}:%{version}-%{release}
Obsoletes:       NetworkManager < %{obsoletes_ppp_plugin}
 
%description ppp
This package contains NetworkManager support for PPP.
%endif

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

make

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
%{_libexecdir}/nm-initrd-generator
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
%{_libexecdir}/nm-daemon-helper
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
%config(noreplace) %{_sysconfdir}/NetworkManager/NetworkManager.conf
%dir %{_localstatedir}/lib/%{name}
%{_sysconfdir}/%{name}/dispatcher.d/10-ifcfg-rh-routes.sh
%{_sysconfdir}/%{name}/dispatcher.d/no-wait.d/10-ifcfg-rh-routes.sh
%{_sysconfdir}/%{name}/dispatcher.d/pre-up.d/10-ifcfg-rh-routes.sh
%{_libdir}/pppd/%{ppp_version}/nm-pppd-plugin.so
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-team.so
%{_bindir}/nmtui*
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-adsl.so
%if %{with nm_cloud_setup}
%{_libexecdir}/nm-cloud-setup
%{systemd_dir}/nm-cloud-setup.service
%{systemd_dir}/nm-cloud-setup.timer
%{_prefix}/lib/%{name}/dispatcher.d/90-nm-cloud-setup.sh
%{_prefix}/lib/%{name}/dispatcher.d/no-wait.d/90-nm-cloud-setup.sh
%endif
%{_prefix}/lib/firewalld/zones/nm-shared.xml
%config(noreplace) /etc/ld.so.conf.d/*

%files wwan
%defattr(-,root,root)
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-wwan.so
%{_libdir}/%{name}/%{version}-%{release}/libnm-wwan.so

%if %{with bluetooth}
%files bluetooth
%defattr(-,root,root)
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-bluetooth.so
%endif

%if %{with wifi}
%files wifi
%defattr(-,root,root)
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-wifi.so
%endif

%if %{with ovs}
%files ovs
%defattr(-,root,root)
%{_libdir}/%{name}/%{version}-%{release}/libnm-device-plugin-ovs.so
%{systemd_dir}/NetworkManager.service.d/NetworkManager-ovs.conf
%endif

%if %{with ppp}
%files ppp
%defattr(-,root,root)
%{_libdir}/%{name}/%{version}-%{release}/libnm-ppp-plugin.so
%endif
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
%doc CONTRIBUTING.md NEWS README TODO
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
* Fri Jul 29 2022 Aichun Li <liaichun@huawei.com> - 1.32.12-10
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:libnm:fix warning when setting wrong ethtool ternary value
core: reload config for active devices
libnm: fix crash on failure of nm_vpn_plugin_info_new_from_file()
libnm: fix crash in _nm_ip_route_validate_all for invalid-route

* Wed Jul 13 2022 gaoxingwang <gaoxingwang1@huawei.com> - 1.32.12-9
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix remove NetworkManager wrongly when yum remove NetworkManager-bluetooth subpackage that is not installed

* Mon Mar 14 2022 gaoxingwang <gaoxingwang@huawei.com> - 1.32.12-8
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:recover to 30s timeout in NetworkManager-wait-online service

* Mon Mar 7 2022 gaoxingwang <gaoxingwang@huawei.com> - 1.32.12-7
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix ipv6 external route miss

* Mon Mar 7 2022 gaoxingwang <gaoxingwang@huawei.com> - 1.32.12-6
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix miss patch

* Sat Feb 26 2022 gaoxingwang <gaoxingwang@huawei.com> - 1.32.12-5
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix the issue that NetworkManager service does not slf-heal when the dbus service is abnormal

* Mon Jan 17 2022 xu_ping <xuping33@huawei.com> - 1.32.12-4
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:Fix D-Bus policy file installed in /usr/share

* Mon Jan 10 2022 gaoxingwang <gaoxingwang@huawei.com> - 1.32.12-3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix build error due to upgrading dependency packages

* Wed Dec 15 2021 gaoxingwang <gaoxingwang@huawei.com> - 1.32.12-2
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:merge multiple modifications into one patch to fix the dependency problem

* Tue Dec 14 2021 gaoxingwang <gaoxingwang@huawei.com> - 1.32.12-1
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:update NetworkManager to 1.32.12 

* Thu Nov 18 2021 gaoxingwang <gaoxingwang@huawei.com> - 1.26.0-11
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix bluetooth,wifi,ovs,ppp module install problem

* Thu Nov 11 2021 zengweifeng <zwfeng@huawei.com> - 1.26.0-10
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix use after free

* Sat Oct 30 2021 zhongxuan2 <zhongxuan2@huawei.com> - 1.26.0-9
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:decoupling bluetooth,wifi,ovs,ppp module

* Sat Sep 11 2021 gaoxingwang <gaoxingwang@huawei.com> - 1.26.0-8
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:remove rpath

* Fri Jul 30 2021 jiazhenyuan <jiazhenyuan@uniontech.com> - 1.26.0-7
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix dbus-daemon error when systemd-resolved service was not enabled

* Thu Apr 29 2021 zengwefeng<zwfeng@huawei.com> - 1.26.0-6
- Type:bugfix
- ID:NA
- SUG:NA
- DESC: fix leaking bearer in connect ready
        disconnect signals in NetworkManager device dispose
        fix wrongly considering ipv6.may fail for ipv4

* Thu Oct 29 2020 gaihuiying <gaihuiying1@huawei.com> - 1.26.0-5
- Type:requirement
- ID:NA
- SUG:NA
- DESC:don't support python2 anymore

* Thu Sep 24 2020 zhouyihang <zhouyihang3@huawei.com> - 1.26.0-4
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:add attribute noreplace for NetworkManager.conf

* Fri Sep 11 2020 yuboyun <yuboyun@huawei.com> - 1.26.0-3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:fix NetworkManager restarting service on dependency failure

* Thu Sep 10 2020 hanzhijun <hanzhijun1@huawei.com> - 1.26.0-2
- solve source url problem

* Fri Jul 31 2020 zhujunhao <zhujunhao8@huawei.com> - 1.26.0-1
- update to 1.26.0

* Thu Jul 30 2020 zhujunhao <zhujunhao8@huawei.com> - 1.24.2-1
- update to 1.24.2

* Thu Jul 2 2020 gaoxingwang <gxw94linux@163.com> - 1.20.10-2
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:delete a useless patch

* Mon Jun 22 2020 zhujunhao <zhujunhao8@huawei.com> - 1.20.10-1
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:update to 1.20.10

* Mon Jun 22 2020 yanan li <liyanan032@huawei.com> - 1.16.0-8
- Fix errors when building with gtk-doc.

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

