# MIB header

%if %{mdvver} <= 201100
%define distsuffix mib
%define disttag %{distsuffix}
Vendor: MIB - Mandriva International Backports
%endif

Packager: Nicolo' Costanza <abitrules@yahoo.it>
# end MIB header

%define kernelversion	3
%define patchlevel	8
# sublevel is now used for -stable patches
%define sublevel	12

# kernel Makefile extraversion is substituted by
# kpatch/kgit wich are either 0 (empty), rc (kpatch), git (kgit)
%define kpatch		0

# kernel.org -gitX patch (only the number after "git")
%define kgit		0

# this is the releaseversion
%define mibrel 	1

# This is only to make life easier for people that creates derivated kernels

%define kname 		kernel-vanilla

%define rpmtag		%{disttag}
%if %kpatch
%if %kgit
%define rpmrel		%mkrel 0.%{kpatch}.%{kgit}.%{mibrel}
%else
%define rpmrel		%mkrel 0.%{kpatch}.%{mibrel}
%endif
%else
#%define rpmrel		%mkrel %{mibrel}
%define rpmrel		%{mibrel}
%endif

# theese two never change, they are used to fool rpm/urpmi/smart
%define fakever		1
%define fakerel		%mkrel 1

# When we are using a pre/rc patch, the tarball is a sublevel -1
%if %kpatch
%define kversion  	%{kernelversion}.%{patchlevel}.%{sublevel}
%if %sublevel
%define tar_ver   	%{kernelversion}.%{patchlevel}
%else
%define tar_ver	  	%{kernelversion}.%(expr %{patchlevel} - 1)
%endif
%else
%define kversion  	%{kernelversion}.%{patchlevel}.%{sublevel}
%define tar_ver   	%{kernelversion}.%{patchlevel}
%endif
%define kverrel   	%{kversion}-%{rpmrel}

# used for not making too long names for rpms or search paths
%if %kpatch
%if %kgit
%define buildrpmrel     0.%{kpatch}.%{kgit}.%{mibrel}%{rpmtag}
%else
%define buildrpmrel     0.%{kpatch}.%{mibrel}%{rpmtag}
%endif
%else
%define buildrpmrel     %{mibrel}%{rpmtag}
%endif

%define buildrel        %{kversion}-%{buildrpmrel}

%define kvanilla_notice NOTE: This kernel has no MIB patches and no third-party drivers.

# having different top level names for packges means that you have to remove them by hard :(
%define top_dir_name    %{kname}-%{_arch}

%define build_dir       ${RPM_BUILD_DIR}/%{top_dir_name}
%define src_dir         %{build_dir}/linux-%{tar_ver}

# disable useless debug rpms...
%define _enable_debug_packages  %{nil}
%define debug_package           %{nil}

# build defines
%define build_doc 1
%define build_source 1
%define build_devel 1

%define build_kernel 1

%define distro_branch %(perl -pe '/(\\d+)\\.(\\d)\\.?(\\d)?/; $_="$1.$2"' /etc/mandriva-release)

# End of user definitions
%{?_without_kernel: %global build_kernel 0}
%{?_without_doc: %global build_doc 0}
%{?_without_source: %global build_source 0}
%{?_without_devel: %global build_devel 0}

%{?_with_kernel: %global build_kernel 1}
%{?_with_doc: %global build_doc 1}
%{?_with_source: %global build_source 1}
%{?_with_devel: %global build_devel 1}


############################################################
### Linker start1 > Check point to build for cooker 2013 ###
############################################################
%if %{mdvver} < 201300
%if %(if [ -z "$CC" ] ; then echo 0; else echo 1; fi)
%define kmake %make CC="$CC"
%else
%define kmake %make
%endif
# there are places where parallel make don't work
%define smake make
%endif

%if %{mdvver} == 201300
%if %cross_compiling
%if %(if [ -z "$CC" ] ; then echo 0; else echo 1; fi)
%define kmake %make ARCH=%target_arch CROSS_COMPILE=%(echo %__cc |sed -e 's,-gcc,-,') CC="$CC" LD="$LD" LDFLAGS="$LDFLAGS"
%else
%define kmake %make ARCH=%target_arch CROSS_COMPILE=%(echo %__cc |sed -e 's,-gcc,-,') LD="$LD" LDFLAGS="$LDFLAGS"
%endif
# there are places where parallel make don't work
%define smake make ARCH=%target_arch CROSS_COMPILE=%(echo %__cc |sed -e 's,-gcc,-,') LD="$LD" LDFLAGS="$LDFLAGS"
%else
%if %(if [ -z "$CC" ] ; then echo 0; else echo 1; fi)
%define kmake %make CC="$CC" LD="$LD" LDFLAGS="$LDFLAGS"
%else
%define kmake %make LD="$LD" LDFLAGS="$LDFLAGS"
%endif
# there are places where parallel make don't work
%define smake make LD="$LD" LDFLAGS="$LDFLAGS"
%endif
%endif
############################################################
###  Linker end1 > Check point to build for cooker 2013  ###
############################################################


# Parallelize xargs invocations on smp machines
%define kxargs xargs %([ -z "$RPM_BUILD_NCPUS" ] \\\
	&& RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"; \\\
	[ "$RPM_BUILD_NCPUS" -gt 1 ] && echo "-P $RPM_BUILD_NCPUS")

# Aliases for amd64 builds (better make source links?)
%define target_cpu	%(echo %{_target_cpu} | sed -e "s/amd64/x86_64/")
%define target_arch	%(echo %{_arch} | sed -e "s/amd64/x86_64/" -e 's/arm.*/arm/')

# src.rpm description
Summary: 	The Linux kernel (the core of the Linux operating system)
Name:           %{kname}
Version:        %{kversion}
Release:        %{rpmrel}
License: 	GPLv2
Group: 		System/Kernel and hardware
ExclusiveArch: 	%{ix86} x86_64 %{arm}
ExclusiveOS: 	Linux
URL: 		https://www.kernel.org/

####################################################################
#
# Sources
#
### This is for full SRC RPM
Source0: 	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.x/linux-%{tar_ver}.tar.xz
Source1: 	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.x/linux-%{tar_ver}.tar.sign

# This is for disabling mrproper and other targets on -devel rpms
Source2:	disable-mrproper-in-devel-rpms.patch

Source4:  	README.kernel-sources
Source5:	kernel-vanilla.rpmlintrc

# Kernel defconfigs
Source20: 	i386_defconfig
Source21: 	x86_64_defconfig
Source22:	arm_defconfig

####################################################################
#
# Patches

#
# Patch0 to Patch100 are for core kernel upgrades.
#

# Pre vanilla patch: ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.%{patchlevel}/testing

%if %sublevel
Patch1:   	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.x/patch-%{kversion}.bz2
Source11: 	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.x/patch-%{kversion}.sign
%endif
%if %kpatch
Patch2:   	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.x/patch-%{kernelversion}.%{patchlevel}.%{prev_sublevel}.bz2
Source12: 	ftp://ftp.kernel.org/pub/linux/kernel/v%{kernelversion}.x/patch-%{kernelversion}.%{patchlevel}.%{prev_sublevel}.sign
%endif

#END
####################################################################

### Global Requires/Provides

%if %{mdvver} == 201300
%define requires1	microcode
%define requires2	dracut >= 026
%define requires3	kmod >= 12
%define requires4	sysfsutils >=  2.1.0-12
%define requires5	kernel-firmware >=  20120219-1
%endif

%if %{mdvver} == 201210
%define requires1	bootloader-utils >= 1.15-8
%define requires2	dracut >= 017-16
%define requires3	kmod >= 7-6
%define requires4	sysfsutils >=  2.1.0-12
%define requires5	kernel-firmware >=  20120219-1
%endif

%if %{mdvver} == 201200
%define requires1	bootloader-utils >= 1.15-8
%define requires2	dracut >= 017-16
%define requires3	module-init-tools >= 3.16-5
%define requires4	sysfsutils >=  2.1.0-12
%define requires5	kernel-firmware >=  20120219-1
%endif

%if %{mdvver} < 201200
%define requires1	bootloader-utils >= 1.13-1
%define requires2	mkinitrd >= 4.2.17-31
%define requires3	module-init-tools >= 3.0-7
%define requires4	sysfsutils >= 1.3.0-1
%define requires5	kernel-firmware >= 20101024-2
%endif

%define kprovides1 	%{kname} = %{kverrel}
%define kprovides2 	kernel = %{tar_ver}
%define kprovides3 	alsa = 1.0.26
%define kprovides_server drbd-api = 88

%define	kobsoletes1	dkms-r8192se <= 0019.1207.2010-2
%define	kobsoletes2	dkms-lzma <= 4.43-32
%define	kobsoletes3	dkms-psb <= 4.41.1-7

# conflict dkms packages that dont support kernel-3.9
# all driver versions must be carefully checked to add
# %define kconflicts1	dkms-broadcom-wl < 5.100.82.xx.yy
# %define kconflicts2	dkms-fglrx < 9.xxx.yy.zz
# %define kconflicts3	dkms-nvidia-current < xxx.yy.zz
# %define kconflicts4	dkms-nvidia304 < 304.xx.yy
%define kconflicts5	dkms-nvidia173 <= 173.14.36
%define kconflicts6	dkms-nvidia96xx <= 96.43.23

Autoreqprov: 		no

# might be useful too:
Suggests:	microcode

BuildRequires: 	gcc 

%if %{mdvver} >= 201210
BuildRequires:	kmod-devel kmod-compat
%else
BuildRequires:	module-init-tools
%endif

%ifarch %{arm}
BuildRequires:	uboot-mkimage
%endif


%description
Source package to build the Linux kernel.

%{kvanilla_notice}


#
# kernel: Symmetric MultiProcessing kernel
#
%if %build_kernel
%package -n %{kname}-%{buildrel}
Version:	%{fakever}
Release:	%{fakerel}
%ifarch %{ix86}
Summary:	Linux Kernel for desktop use with i586 & 4GB RAM
%else
%ifarch %{arm}
		Linux Kernel for Arm machines based on Kirkwood
%else
Summary:	Linux Kernel for desktop use with %{_arch}
%endif
%endif
Group:		System/Kernel and hardware

Provides:	should-restart = system

Provides:	%kprovides1 %kprovides2 %kprovides3 %kprovides_server
Provides:   	kernel-desktop              		
Requires(pre):	%requires1 %requires2 %requires3 %requires4 %requires5
Requires:	%requires2 %requires5 			
Obsoletes:	%kobsoletes1 %kobsoletes2 %kobsoletes3
Conflicts:	%kconflicts5 %kconflicts6


%ifarch %{ix86}
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-%{buildrel}
%ifarch %{ix86}
This kernel is compiled for desktop use, single or multiple i586
processor(s)/core(s) and less than 4GB RAM, using HZ_1000, voluntary
preempt, CFS cpu scheduler and cfq i/o scheduler.
This kernel relies on in-kernel smp alternatives to switch between
up & smp mode depending on detected hardware. To force the kernel
to boot in single processor mode, use the "nosmp" boot parameter.
%else
%ifarch %{arm}
This kernel is compiled for Arm Kirkwood boxes. It will run on openrd
boards. It's configured using HZ_100, preempt, CFS cpu scheduler and
cfq i/o scheduler.
This kernel relies on in-kernel smp alternatives to switch between
up & smp mode depending on detected hardware. To force the kernel
to boot in single processor mode, use the "nosmp" boot parameter.
%else
This kernel is compiled for desktop use, single or multiple %{_arch}
processor(s)/core(s), using HZ_1000, voluntary preempt, CFS cpu
scheduler and cfq i/o scheduler.
This kernel relies on in-kernel smp alternatives to switch between
up & smp mode depending on detected hardware. To force the kernel
to boot in single processor mode, use the "nosmp" boot parameter.
%endif
%endif

%{kvanilla_notice}
%endif # build_kernel


#
# kernel-source: kernel sources
#
%if %build_source
%package -n %{kname}-source-%{buildrel}
Version:	%{fakever}
Release:	%{fakerel}
Provides:	%{kname}-source, kernel-source = %{kverrel}
Provides:	%{kname}-source-%{kernelversion}.%{patchlevel}
Requires:	glibc-devel, ncurses-devel, make, gcc, perl, diffutils
Summary:	The source code for the Linux kernel
Group:		Development/Kernel
Autoreqprov: 	no
Buildarch:	noarch

%description -n %{kname}-source-%{buildrel}
The %{kname}-source package contains the source code files for the
Linux kernel. Theese source files are only needed if you want to build
your own custom kernel that is better tuned to your particular hardware.

If you only want the files needed to build 3rdparty (nVidia, Ati, dkms-*,...)
drivers against, install the *-devel-* rpm that is matching your kernel.

%{kvanilla_notice}
%endif #build_source


#
# kernel-devel: stripped kernel sources
#
%if %build_devel
%package -n %{kname}-devel-%{buildrel}
Version:	%{fakever}
Release:	%{fakerel}
Provides:	kernel-devel = %{kverrel}
Summary:	The %{kname} devel files for 3rdparty modules build
Group:		Development/Kernel
Autoreqprov:	no
Requires:	glibc-devel, ncurses-devel, make, gcc, perl
%ifarch %{ix86}
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-devel-%{buildrel}
This package contains the kernel-devel files that should be enough to build
3rdparty drivers against for use with the %{kname}-%{buildrel}.

If you want to build your own kernel, you need to install the full
%{kname}-source-%{buildrel} rpm.

%{kvanilla_notice}
%endif #build_devel


#
# kernel-doc: documentation for the Linux kernel
#
%if %build_doc
%package -n %{kname}-doc
Version:        %{kversion}
Release:        %{rpmrel}
Summary:	Various documentation bits found in the kernel source
Group:		Documentation
Buildarch:	noarch

%description -n %{kname}-doc
This package contains documentation files form the kernel source. Various
bits of information about the Linux kernel and the device drivers shipped
with it are documented in these files. You also might want install this
package if you need a reference to the options that can be passed to Linux
kernel modules at load time.

%{kvanilla_notice}
%endif #build_doc


#
# kernel-latest: virtual rpm
#
%if %build_kernel
%package -n %{kname}-latest
Version:        %{kversion}
Release:        %{rpmrel}
Summary: 	Virtual rpm for latest %{kname}
Group: 	  	System/Kernel and hardware
Requires: 	%{kname}-%{buildrel}
%ifarch %{ix86}
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-latest
This package is a virtual rpm that aims to make sure you always have the
latest %{kname} installed...

%{kvanilla_notice}
%endif #build_kernel


#
# kernel-source-latest: virtual rpm
#
%if %build_source
%package -n %{kname}-source-latest
Version:        %{kversion}
Release:        %{rpmrel}
Summary: 	Virtual rpm for latest %{kname}-source
Group: 	  	System/Kernel and hardware
Requires: 	%{kname}-source-%{buildrel}
Buildarch:	noarch

%description -n %{kname}-source-latest
This package is a virtual rpm that aims to make sure you always have the
latest %{kname}-source installed...

%{kvanilla_notice}
%endif #build_source


#
# kernel-devel-latest: virtual rpm
#
%if %build_devel
%package -n %{kname}-devel-latest
Version:        %{kversion}
Release:        %{rpmrel}
Summary: 	Virtual rpm for latest %{kname}-devel
Group: 	  	System/Kernel and hardware
Requires: 	%{kname}-devel-%{buildrel}
%ifarch %{ix86}
Conflicts:	arch(x86_64)
%endif

%description -n %{kname}-devel-latest
This package is a virtual rpm that aims to make sure you always have the
latest %{kname}-devel installed...

%{kvanilla_notice}
%endif #build_devel


#
# End packages - here begins build stage
#
%prep
%setup -q -n %top_dir_name -c

pushd %src_dir

%if %sublevel
%patch1 -p1
%endif
%if %kpatch
%patch2 -p1
%endif

popd

# PATCH END


#
# Setup Begin
#


# Install defconfigs...
install %{SOURCE20} %{build_dir}/linux-%{tar_ver}/arch/x86/configs/
install %{SOURCE21} %{build_dir}/linux-%{tar_ver}/arch/x86/configs/
install %{SOURCE22} %{build_dir}/linux-%{tar_ver}/arch/arm/configs/

# make sure the kernel has the sublevel we know it has...
LC_ALL=C perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{sublevel}/" linux-%{tar_ver}/Makefile


%build

############################################################
### Linker start2 > Check point to build for cooker 2013 ###
############################################################
%if %{mdvver} == 201300
# Make sure we don't use gold
export LD="%{_target_platform}-ld.bfd"
export LDFLAGS="--hash-style=sysv --build-id=none"
%endif
############################################################
###  Linker end2 > Check point to build for cooker 2013  ###
############################################################

# Common target directories
%define _bootdir /boot
%define _modulesdir /lib/modules
%define _kerneldir /usr/src/%{kname}-%{buildrel}
%define _develdir /usr/src/%{kname}-devel-%{buildrel}


# Directories definition needed for building
%define temp_root %{build_dir}/temp-root
%define temp_boot %{temp_root}%{_bootdir}
%define temp_modules %{temp_root}%{_modulesdir}
%define temp_source %{temp_root}%{_kerneldir}
%define temp_devel %{temp_root}%{_develdir}


# Create a simulacro of buildroot
rm -rf %{temp_root}
install -d %{temp_root}


# make sure we are in the directory
cd %{src_dir}

# make sure EXTRAVERSION says what we want it to say
LC_ALL=C perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{buildrpmrel}/" Makefile

# Prepare the kernel
%smake -s mrproper
%ifarch %{ix86} x86_64
	cp arch/x86/configs/%{target_arch}_defconfig .config
%else
	cp arch/%{target_arch}/%{target_arch}_defconfig .config
%endif
%smake oldconfig

# Build the kernel
%kmake -s all
%ifarch %{arm}
	%kmake uImage
%endif
# Install kernel
install -d %{temp_boot}
install -m 644 System.map %{temp_boot}/System.map-%{buildrel}
install -m 644 .config %{temp_boot}/config-%{buildrel}
%ifarch %{arm}
	cp -f arch/%{target_arch}/boot/uImage %{temp_boot}/uImage-$KernelVer
%else
	cp -f arch/%{target_arch}/boot/bzImage %{temp_boot}/vmlinuz-%{buildrel}
%endif

# Install modules
install -d %{temp_modules}/%{buildrel}
%smake INSTALL_MOD_PATH=%{temp_root} KERNELRELEASE=%{buildrel} modules_install

# remove /lib/firmware, we use a separate kernel-firmware
rm -rf %{temp_root}/lib/firmware

# Save devel tree
%if %build_devel
mkdir -p %{temp_devel}
for i in $(find . -name 'Makefile*'); do cp -R --parents $i %{temp_devel};done
for i in $(find . -name 'Kconfig*' -o -name 'Kbuild*' -o -name config.mk); do cp -R --parents $i %{temp_devel};done
cp -fR include %{temp_devel}
cp -fR scripts %{temp_devel}
cp -fR tools/include %{temp_devel}/tools/
%ifarch %{arm}
	cp -fR arch/%{target_arch}/tools $TempDevelRoot/arch/%{target_arch}/
%endif
%ifarch %{ix86} x86_64
	cp -fR arch/x86/kernel/asm-offsets.{c,s} %{temp_devel}/arch/x86/kernel/
	cp -fR arch/x86/kernel/asm-offsets_{32,64}.c %{temp_devel}/arch/x86/kernel/
	cp -fR arch/x86/syscalls/syscall* %{temp_devel}/arch/x86/syscalls/
	cp -fR arch/x86/include %{temp_devel}/arch/x86/
	cp -fR arch/x86/tools/relocs.c %{temp_devel}/arch/x86/tools/
%else
	cp -fR arch/%{target_arch}/kernel/asm-offsets.{c,s} %{temp_devel}/arch/%{target_arch}/kernel/
	for f in $(find arch/%{target_arch} -name include); do cp -fR --parents $f $TempDevelRoot; done
%endif

# Needed for generation of kernel/bounds.s
cp -fR kernel/bounds.c %{temp_devel}/kernel/

# Needed for lguest
cp -fR drivers/lguest/lg.h %{temp_devel}/drivers/lguest/

cp -fR .config Module.symvers %{temp_devel}

# Needed for truecrypt build (Danny)
cp -fR drivers/md/dm.h %{temp_devel}/drivers/md/

# Needed for external dvb tree (#41418)
cp -fR drivers/media/dvb-core/*.h %{temp_devel}/drivers/media/dvb-core/
cp -fR drivers/media/dvb-frontends/lgdt330x.h %{temp_devel}/drivers/media/dvb-frontends/

# add acpica header files, needed for fglrx build
cp -fR drivers/acpi/acpica/*.h %{temp_devel}/drivers/acpi/acpica/

# Check and clean the -devel tree
pushd %{temp_devel} >/dev/null
    %smake -s prepare scripts clean
    rm -f .config.old
popd >/dev/null

# Disable mrproper and other targets
patch -p1 -d %{temp_devel} -i %{SOURCE2}

# Fix permissions
chmod -R a+rX %{temp_devel}
%endif # build_devel

#make sure we are in the directory
cd %src_dir

# kernel-source is shipped as an unprepared tree
%smake -s mrproper


###
### Install
###
%install
install -m 644 %{SOURCE4}  .

cd %src_dir
# Directories definition needed for installing
%define target_source %{buildroot}/%{_kerneldir}
%define target_boot %{buildroot}%{_bootdir}
%define target_modules %{buildroot}%{_modulesdir}
%define target_devel %{buildroot}%{_develdir}

# We want to be able to test several times the install part
rm -rf %{buildroot}
cp -a %{temp_root} %{buildroot}

# Create directories infastructure
%if %build_source
install -d %{target_source}

tar cf - . | tar xf - -C %{target_source}
chmod -R a+rX %{target_source}

# we remove all the source files that we don't ship

# first architecture files
for i in alpha avr32 blackfin c6x cris frv hexagon h8300 ia64 m32r mips \
	 microblaze m68k m68knommu mn10300 openrisc parisc powerpc ppc \
	 s390 score sh sh64 sparc tile unicore32 v850 xtensa; do
	rm -rf %{target_source}/arch/$i

%if %build_devel
	rm -rf %{target_devel}/arch/$i
%endif
done

# remove arch files based on target arch in -devel rpms
%if %build_devel
%ifnarch %{ix86} x86_64
	rm -rf %{target_devel}/arch/x86
%endif
%ifnarch %{arm}
	rm -rf %{target_devel}/arch/arm
	rm -rf %{target_devel}/arch/arm64
%endif
%endif


# other misc files
rm -f %{target_source}/{.config.old,.config.cmd,.tmp_gas_check,.mailmap,.missing-syscalls.d,arch/.gitignore}
rm -rf %{target_source}/.tmp_depmod/

#endif %build_source
%endif


# compressing modules
find %{target_modules} -name "*.ko" | %kxargs xz -6e


# We used to have a copy of PrepareKernel here
# Now, we make sure that the thing in the linux dir is what we want it to be

for i in %{target_modules}/*; do
  rm -f $i/build $i/source
done


# sniff, if we gzipped all the modules, we change the stamp :(
# we really need the depmod -ae here
pushd %{target_modules}
for i in *; do
	/sbin/depmod -ae -b %{buildroot} -F %{target_boot}/System.map-$i $i
	echo $?
done

for i in *; do
	pushd $i
	echo "Creating module.description for $i"
	modules=`find . -name "*.ko.xz"`
	echo $modules | %kxargs /sbin/modinfo \
	| perl -lne 'print "$name\t$1" if $name && /^description:\s*(.*)/; $name = $1 if m!^filename:\s*(.*)\.k?o!; $name =~ s!.*/!!' > modules.description
	popd
done
popd


###
### Clean
###

%clean
rm -rf %{buildroot}
# We don't want to remove this, the whole reason of its existence is to be
# able to do several rpm --short-circuit -bi for testing install 
# phase without repeating compilation phase
#rm -rf %{temp_root}


###
### Scripts
###

### kernel
%if %build_kernel
%preun -n %{kname}-%{buildrel}
/sbin/installkernel -R %{buildrel}
if [ -L /lib/modules/%{buildrel}/build ]; then
    rm -f /lib/modules/%{buildrel}/build
fi
if [ -L /lib/modules/%{buildrel}/source ]; then
    rm -f /lib/modules/%{buildrel}/source
fi
pushd /boot > /dev/null
if [ -L vmlinuz-vanilla ]; then
    if [ "$(readlink vmlinuz-vanilla)" = "vmlinuz-%{buildrel}" ]; then
	rm -f vmlinuz-vanilla
    fi
fi
if [ -L initrd-vanilla.img ]; then
    if [ "$(readlink initrd-vanilla.img)" = "initrd-%{buildrel}.img" ]; then
	rm -f initrd-vanilla.img
    fi
fi
popd > /dev/null
exit 0

%post -n %{kname}-%{buildrel}
/sbin/installkernel -L %{buildrel}
if [ -d /usr/src/%{kname}-devel-%{buildrel} ]; then
    ln -sf /usr/src/%{kname}-devel-%{buildrel} /lib/modules/%{buildrel}/build
    ln -sf /usr/src/%{kname}-devel-%{buildrel} /lib/modules/%{buildrel}/source
fi
pushd /boot > /dev/null
if [ -L vmlinuz-vanilla ]; then
    rm -f vmlinuz-vanilla
fi
ln -sf vmlinuz-%{buildrel} vmlinuz-vanilla
if [ -L initrd-vanilla.img ]; then
    rm -f initrd-vanilla.img
fi
ln -sf initrd-%{buildrel}.img initrd-vanilla.img
popd > /dev/null

%posttrans -n %{kname}-%{buildrel}
if [ -x /usr/sbin/dkms_autoinstaller -a -d /usr/src/%{kname}-devel-%{buildrel} ]; then
    /usr/sbin/dkms_autoinstaller start %{buildrel}
fi

%postun -n %{kname}-%{buildrel}
/sbin/kernel_remove_initrd %{buildrel}
rm -rf /lib/modules/%{buildrel} > /dev/null
%endif # build_kernel


### kernel-devel
%if %build_devel
%post -n %{kname}-devel-%{buildrel}
# place /build and /source symlinks in place.
if [ -d /lib/modules/%{buildrel} ]; then
    ln -sf /usr/src/%{kname}-devel-%{buildrel} /lib/modules/%{buildrel}/build
    ln -sf /usr/src/%{kname}-devel-%{buildrel} /lib/modules/%{buildrel}/source
fi

%preun -n %{kname}-devel-%{buildrel}
# we need to delete <modules>/{build,source} at uninstall
if [ -L /lib/modules/%{buildrel}/build ]; then
    rm -f /lib/modules/%{buildrel}/build
fi
if [ -L /lib/modules/%{buildrel}/source ]; then
    rm -f /lib/modules/%{buildrel}/source
fi
exit 0
%endif #build_devel


###
### file lists
###

# kernel
%if %build_kernel
%files -n %{kname}-%{buildrel}
%{_bootdir}/config-%{buildrel}
%ifarch %{arm}
%{_bootdir}/uImage-%{buildrel}
%else
%{_bootdir}/vmlinuz-%{buildrel}
%endif
%{_bootdir}/System.map-%{buildrel}
%dir %{_modulesdir}/%{buildrel}/
%{_modulesdir}/%{buildrel}/kernel
%{_modulesdir}/%{buildrel}/modules.*
%doc README.kernel-sources
%endif # build_kernel

# kernel-source
%if %build_source
%files -n %{kname}-source-%{buildrel}
%dir %{_kerneldir}
%dir %{_kerneldir}/arch
%dir %{_kerneldir}/include
%{_kerneldir}/.gitignore
%{_kerneldir}/COPYING
%{_kerneldir}/CREDITS
%{_kerneldir}/Documentation
%{_kerneldir}/Kbuild
%{_kerneldir}/Kconfig
%{_kerneldir}/MAINTAINERS
%{_kerneldir}/Makefile
%{_kerneldir}/README
%{_kerneldir}/REPORTING-BUGS
%{_kerneldir}/arch/Kconfig
#%{_kerneldir}/arch/arc
%{_kerneldir}/arch/arm
%{_kerneldir}/arch/arm64
#%{_kerneldir}/arch/metag
%{_kerneldir}/arch/x86
%{_kerneldir}/arch/um
%{_kerneldir}/block
%{_kerneldir}/crypto
%{_kerneldir}/drivers
%{_kerneldir}/firmware
%{_kerneldir}/fs
%{_kerneldir}/include/Kbuild
%{_kerneldir}/include/acpi
%{_kerneldir}/include/asm-generic
%{_kerneldir}/include/clocksource
%{_kerneldir}/include/crypto
%{_kerneldir}/include/drm
%{_kerneldir}/include/linux
%{_kerneldir}/include/math-emu
%{_kerneldir}/include/memory
%{_kerneldir}/include/net
%{_kerneldir}/include/pcmcia
%{_kerneldir}/include/ras
%{_kerneldir}/include/scsi
%{_kerneldir}/include/sound
%{_kerneldir}/include/target
%{_kerneldir}/include/trace
%{_kerneldir}/include/uapi
%{_kerneldir}/include/video
%{_kerneldir}/include/media
%{_kerneldir}/include/misc
%{_kerneldir}/include/rxrpc
%{_kerneldir}/include/keys
%{_kerneldir}/include/rdma
%{_kerneldir}/include/xen
%{_kerneldir}/init
%{_kerneldir}/ipc
%{_kerneldir}/kernel
%{_kerneldir}/lib
%{_kerneldir}/mm
%{_kerneldir}/net
%{_kerneldir}/samples
%{_kerneldir}/scripts
%{_kerneldir}/security
%{_kerneldir}/sound
%{_kerneldir}/tools
%{_kerneldir}/usr
%{_kerneldir}/virt
%doc README.kernel-sources
%endif # build_source

# kernel-devel
%if %build_devel
%files -n %{kname}-devel-%{buildrel}
%dir %{_develdir}
%dir %{_develdir}/arch
%dir %{_develdir}/include
%{_develdir}/.config
%{_develdir}/Documentation
%{_develdir}/Kbuild
%{_develdir}/Kconfig
%{_develdir}/Makefile
%{_develdir}/Module.symvers
%{_develdir}/arch/Kconfig
%ifarch %{arm}
%{_develdir}/arch/arm
%{_develdir}/arch/arm64
%endif
%ifarch %{ix86} x86_64
%{_develdir}/arch/x86
%endif
%{_develdir}/arch/um
%{_develdir}/block
%{_develdir}/crypto
%{_develdir}/drivers
%{_develdir}/firmware
%{_develdir}/fs
%{_develdir}/include/Kbuild
%{_develdir}/include/acpi
%{_develdir}/include/asm-generic
%{_develdir}/include/clocksource
%{_develdir}/include/config
%{_develdir}/include/crypto
%{_develdir}/include/drm
%{_develdir}/include/generated
%{_develdir}/include/keys
%{_develdir}/include/linux
%{_develdir}/include/math-emu
%{_develdir}/include/memory
%{_develdir}/include/misc
%{_develdir}/include/net
%{_develdir}/include/pcmcia
%{_develdir}/include/ras
%{_develdir}/include/rdma
%{_develdir}/include/scsi
%{_develdir}/include/sound
%{_develdir}/include/target
%{_develdir}/include/trace
%{_develdir}/include/uapi
%{_develdir}/include/video
%{_develdir}/include/media
%{_develdir}/include/rxrpc
%{_develdir}/include/xen
%{_develdir}/init
%{_develdir}/ipc
%{_develdir}/kernel
%{_develdir}/lib
%{_develdir}/mm
%{_develdir}/net
%{_develdir}/samples
%{_develdir}/scripts
%{_develdir}/security
%{_develdir}/sound
%{_develdir}/tools
%{_develdir}/usr
%{_develdir}/virt
%doc README.kernel-sources
%endif # build_devel


%if %build_doc
%files -n %{kname}-doc
%doc linux-%{tar_ver}/Documentation/*
%endif # build_doc

%if %build_kernel
%files -n %{kname}-latest
%endif # build_kernel

%if %build_source
%files -n %{kname}-source-latest
%endif # build_source

%if %build_devel
%files -n %{kname}-devel-latest
%endif # build_devel


%changelog

* Thu May 09 2013 Nicolo' Costanza <abitrules@yahoo.it> 3.8.12-1
+ kernel 3.8.12 vanilla stable 
- prepared the first package for kernel-vanilla 3.8
- ---------------------------------------------------------------------
- Kernel 3.8 for mdv 2010.2, 2011.0, cooker, rosa.lts2012.0, rosa2012.1
- MIB (Mandriva International Backports) - http://mib.pianetalinux.org/
- This kernel has no MIB or other patches, and no third-party drivers
- ---------------------------------------------------------------------