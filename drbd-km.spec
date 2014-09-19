# "uname -r" output of the kernel to build for, the running one
# if none was specified with "--define 'kernelversion <uname -r>'"
# PLEASE: provide both (correctly) or none!!
%{!?kernelversion: %{expand: %%define kernelversion %(uname -r)}}
%{!?kdir: %{expand: %%define kdir /lib/modules/%(uname -r)/build}}

# encode - to _ to be able to include that in a package name or release "number"
%global krelver  %(echo %{kernelversion} | tr -s '-' '_')

Name: drbd-km
Summary: DRBD driver for Linux
Version: 9.0.0pre10
Release: 1
Source: http://oss.linbit.com/%{name}/8.3/drbd-%{version}.tar.gz
License: GPLv2+
ExclusiveOS: linux
Group: System Environment/Kernel
URL: http://www.drbd.org/
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if 0%{?suse_version} || 0%{?sles_version}
BuildRequires: gcc, kernel-syms
%endif
%if 0%{?fedora} || 0%{?rhel_version} || 0%{?centos_version}
BuildRequires: gcc, kernel-devel
%endif

%description
DRBD mirrors a block device over the network to another machine.
Think of it as networked raid 1. It is a building block for
setting up high availability (HA) clusters.

# I choose to have the kernelversion as part of the package name!
# drbd-km is prepended...
%package %{krelver}
Summary: Kernel driver for DRBD.
Group: System Environment/Kernel

%if 0%{?suse_version} || 0%{?sles_version}
Conflicts: km_drbd, drbd-kmp <= %{version}_3
%endif
%if 0%{?fedora} || 0%{?rhel_version} || 0%{?centos_version}
Conflicts: drbd-kmod <= %{version}_3
%endif


# always require a suitable userland and depmod.
Requires: drbd-utils = %{version}, /sbin/depmod
# to be able to override from build scripts which flavor of kernel we are building against.
Requires: %{expand: %(echo ${DRBD_KMOD_REQUIRES:-kernel})}
# TODO: break up this generic .spec file into per distribution ones,
# and use the distribution specific naming and build conventions for kernel modules.

%description %{krelver}
This module is the kernel-dependent driver for DRBD.  This is split out so
that multiple kernel driver versions can be installed, one for each
installed kernel.

%files %{krelver}
%defattr(-,root,root)
/lib/modules/%{kernelversion}/
%doc COPYING
%doc ChangeLog
%doc drbd/k-config-%{kernelversion}.gz

%prep
%setup -q -n drbd-%{version}
test -d %{kdir}/.
test "$(KDIR=%{kdir} scripts/get_uts_release.sh)" = %{kernelversion}

%build
echo kernelversion=%{kernelversion}
echo kversion=%{kversion}
echo krelver=%{krelver}
make %{_smp_mflags} module KDIR=%{kdir}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
cd drbd
mv .kernel.config.gz k-config-%{kernelversion}.gz

%clean
rm -rf %{buildroot}

%preun %{krelver}
lsmod | grep drbd > /dev/null 2>&1
if [ $? -eq 0 ]; then
    rmmod drbd
fi

%post %{krelver}
# hack for distribution kernel packages,
# which already contain some (probably outdated) drbd module
EXTRA_DRBD_KO=/lib/modules/%{kernelversion}/extra/drbd.ko
if test -e $EXTRA_DRBD_KO; then
    mv $EXTRA_DRBD_KO $EXTRA_DRBD_KO.orig
fi
uname -r | grep BOOT ||
/sbin/depmod -a -F /boot/System.map-%{kernelversion} %{kernelversion} >/dev/null 2>&1 || true

%postun %{krelver}
/sbin/depmod -a -F /boot/System.map-%{kernelversion} %{kernelversion} >/dev/null 2>&1 || true


%changelog
* Fri Sep 19 2014 Philipp Reisner <phil@linbit.com> - 9.0.0pre10-1
- New upstream release.

* Fri Mar  7 2014 Philipp Reisner <phil@linbit.com> - 9.0.0pre9-1
- New upstream release.

* Thu Feb  6 2014 Philipp Reisner <phil@linbit.com> - 9.0.0pre8-1
- New upstream release.

* Sun Dec 22 2013 Philipp Reisner <phil@linbit.com> - 9.0.0pre7-1
- New upstream release.

* Wed Aug 14 2013 Philipp Reisner <phil@linbit.com> - 9.0.0pre6-1
- New upstream release.

* Fri Jul 12 2013 Philipp Reisner <phil@linbit.com> - 9.0.0pre5-1
- New upstream release.

* Fri May 31 2013 Philipp Reisner <phil@linbit.com> - 9.0.0pre4-1
- New upstream release.

* Tue Apr 30 2013 Philipp Reisner <phil@linbit.com> - 9.0.0pre3-1
- New upstream release.

* Mon Apr 15 2013 Philipp Reisner <phil@linbit.com> - 9.0.0pre2-1
- New upstream release.

* Mon Dec  3 2012 Philipp Reisner <phil@linbit.com> - 9.0.0pre1-1
- New upstream release.

* Mon Jul 18 2011 Philipp Reisner <phil@linbit.com> - 8.4.0-1
- New upstream release.

* Fri Jan 28 2011 Philipp Reisner <phil@linbit.com> - 8.3.10-1
- New upstream release.

* Fri Oct 22 2010 Philipp Reisner <phil@linbit.com> - 8.3.9-1
- New upstream release.

* Wed Jun  2 2010 Philipp Reisner <phil@linbit.com> - 8.3.8-1
- New upstream release.

* Wed Jan 13 2010 Philipp Reisner <phil@linbit.com> - 8.3.7-1
- New upstream release.

* Sun Nov  8 2009 Philipp Reisner <phil@linbit.com> - 8.3.6-1
- New upstream release.

* Tue Oct 27 2009 Philipp Reisner <phil@linbit.com> - 8.3.5-1
- New upstream release.

* Wed Oct 21 2009 Florian Haas <florian@linbit.com> - 8.3.4-12
- Packaging makeover.

* Tue Oct  6 2009 Philipp Reisner <phil@linbit.com> - 8.3.4-1
- New upstream release.

* Mon Oct  5 2009 Philipp Reisner <phil@linbit.com> - 8.3.3-1
- New upstream release.

* Fri Jul  3 2009 Philipp Reisner <phil@linbit.com> - 8.3.2-1
- New upstream release.

* Fri Mar 27 2009 Philipp Reisner <phil@linbit.com> - 8.3.1-1
- New upstream release.

* Thu Dec 18 2008 Philipp Reisner <phil@linbit.com> - 8.3.0-1
- New upstream release.

* Wed Nov 12 2008 Philipp Reisner <phil@linbit.com> - 8.2.7-1
- New upstream release.

* Fri May 30 2008 Philipp Reisner <phil@linbit.com> - 8.2.6-1
- New upstream release.

* Tue Feb 12 2008 Philipp Reisner <phil@linbit.com> - 8.2.5-1
- New upstream release.

* Fri Jan 11 2008 Philipp Reisner <phil@linbit.com> - 8.2.4-1
- New upstream release.

* Wed Jan  9 2008 Philipp Reisner <phil@linbit.com> - 8.2.3-1
- New upstream release.

* Fri Nov  2 2007 Philipp Reisner <phil@linbit.com> - 8.2.1-1
- New upstream release.

* Fri Sep 28 2007 Philipp Reisner <phil@linbit.com> - 8.2.0-1
- New upstream release.

* Mon Sep  3 2007 Philipp Reisner <phil@linbit.com> - 8.0.6-1
- New upstream release.

* Fri Aug  3 2007 Philipp Reisner <phil@linbit.com> - 8.0.5-1
- New upstream release.

* Wed Jun 27 2007 Philipp Reisner <phil@linbit.com> - 8.0.4-1
- New upstream release.

* Mon May 7 2007 Philipp Reisner <phil@linbit.com> - 8.0.3-1
- New upstream release.

* Fri Apr 6 2007 Philipp Reisner <phil@linbit.com> - 8.0.2-1
- New upstream release.

* Mon Mar  5 2007 Philipp Reisner <phil@linbit.com> - 8.0.1-1
- New upstream release.

* Wed Jan 24 2007 Philipp Reisner <phil@linbit.com>  - 8.0.0-1
- New upstream release.

