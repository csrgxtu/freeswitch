# Copyright (c) 2000, 2013, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston
# MA  02110-1301  USA.

##############################################################################
#
# mysql-connector-odbc 5.3 RPM specification
#
##############################################################################

%global mysql_vendor	Oracle and/or its affiliates

%if 0%{?commercial}
%global license_type	Commercial
%global license_files	LICENSE.mysql
%global product_suffix	-commercial
%else
%global license_type	GPLv2
%global license_files	COPYING
%endif

# Use rpmbuild -ba --define 'shared_mysqlclient 1' ... to build shared
%{!?shared_mysqlclient: %global static_mysqlclient 1}

##############################################################################
#
#  Main information section
#
##############################################################################

Summary:	An ODBC 5.3 driver for MySQL - driver package
Name:		mysql-connector-odbc%{?product_suffix}
Version:	5.3.4
Release:	1%{?dist}
License:	Copyright (c) 2000, 2014, %{mysql_vendor}. All rights reserved.  Under %{license_type} license as shown in the Description field.
Source0:	http://cdn.mysql.com/Downloads/Connector-ODBC/5.3/%{name}-5.3.4-src.tar.gz
URL:		http://www.mysql.com/
Group:		Applications/Databases
Vendor:		%{mysql_vendor}
Packager:	%{mysql_vendor} Product Engineering Team <mysql-build@oss.oracle.com>
BuildRequires:	cmake 
%{?shared_mysqlclient:BuildRequires: mysql-community-devel}
BuildRequires:	unixODBC-devel
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if 0%{?odbc_gui}
%package setup
Summary:	An ODBC 5.3 driver for MySQL - setup library
Group:		Application/Databases
Requires:	%{name} = %{version}-%{release}
%endif

%package test
Summary:	An ODBC 5.3 driver for MySQL - tests
Group:		Application/Databases
Requires:	%{name} = %{version}-%{release}

##############################################################################
#
#  Documentation
#
##############################################################################

%description
mysql-connector-odbc is an ODBC (3.51) driver for connecting an ODBC-aware
application to MySQL. mysql-connector-odbc works on Windows XP/Vista/7/8
Windows Server 2003/2008/2012, and most Unix platforms (incl. OSX and Linux).
MySQL is a trademark of %{mysql_vendor}

mysql-connector-odbc 5.3 is an enhanced version of mysql-connector-odbc 5.2.
The driver comes in 2 flavours - ANSI and Unicode and commonly referred to as
'MySQL ODBC 5.3 ANSI Driver' or 'MySQL ODBC 5.3 Unicode Driver' respectively.

The MySQL software has Dual Licensing, which means you can use the
MySQL software free of charge under the GNU General Public License
(http://www.gnu.org/licenses/). You can also purchase commercial MySQL
licenses from %{mysql_vendor} if you do not wish to be bound by the
terms of the GPL. See the chapter "Licensing and Support" in the
manual for further info.

The MySQL web site (http://www.mysql.com/) provides the latest news
and information about the MySQL software. Also please see the
documentation and the manual for more information.

%if 0%{?odbc_gui}
%description setup
The setup library for the MySQL ODBC package, handles the optional GUI
dialog for configuring the driver.
%endif

%description test
The test suite for MySQL ODBC.

##############################################################################
#
#  Build
#
##############################################################################

%prep
%setup -q -n %{name}-5.3.4-src

%build
mkdir release
pushd release
export CFLAGS="%{optflags}"
cmake -G "Unix Makefiles"   \
    -DRPM_BUILD=1           \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
%if 0%{?odbc_gui}
%else
    -DDISABLE_GUI=1         \
%endif
%if 0%{?unixodbc}
    -DWITH_UNIXODBC=1       \
%endif
    %{?cmake_opt_extra}      \
    ..

# Note that the ".." needs to be last, in case some arguments expands to 
# the empty string, and then "cmake" thinks is "current directory"

make  %{?_smp_mflags} VERBOSE=1
popd

##############################################################################
#
#  Cleanup
#
##############################################################################

%clean
rm -rf %{buildroot}

##############################################################################
#
#  Install and deinstall scripts
#
##############################################################################

# ----------------------------------------------------------------------
# Install, but remove the doc files.
# The way %doc <file-without-path> works, we can't
# have these files installed
# ----------------------------------------------------------------------

%install
pushd release
make DESTDIR=%{buildroot} install VERBOSE=1
rm -vf  %{buildroot}%{_prefix}/{ChangeLog,README*,LICENSE.*,COPYING,INSTALL*,Licenses_for_Third-Party_Components.txt}
mkdir -p %{buildroot}%{_datadir}/mysql-connector-odbc
mv %{buildroot}%{_prefix}/test %{buildroot}%{_datadir}/mysql-connector-odbc/
mv bin/dltest %{buildroot}%{_bindir}/
popd

# ----------------------------------------------------------------------
# REGISTER DRIVER
# Note that "-e" is not working for drivers currently, so we have to
# deinstall before reinstall to change anything
# ----------------------------------------------------------------------

%post 
if [ -x /usr/bin/myodbc-installer ]; then
    /usr/bin/myodbc-installer -a -d -n "MySQL ODBC 5.3 Unicode Driver" -t "DRIVER=%{_libdir}/libmyodbc5w.so"
    /usr/bin/myodbc-installer -a -d -n "MySQL ODBC 5.3 ANSI Driver"    -t "DRIVER=%{_libdir}/libmyodbc5a.so"
fi

%if 0%{?odbc_gui}
%post setup
/usr/bin/myodbc-installer -r -d -n "MySQL ODBC 5.3 Unicode Driver"
/usr/bin/myodbc-installer -r -d -n "MySQL ODBC 5.3 ANSI Driver"
/usr/bin/myodbc-installer -a -d -n "MySQL ODBC 5.3 Unicode Driver" -t "DRIVER=%{_libdir}/libmyodbc5w.so;SETUP=%{_libdir}/libmyodbc5S.so"
/usr/bin/myodbc-installer -a -d -n "MySQL ODBC 5.3 ANSI Driver"    -t "DRIVER=%{_libdir}/libmyodbc5a.so;SETUP=%{_libdir}/libmyodbc5S.so"
%endif

# ----------------------------------------------------------------------
# DEREGISTER DRIVER 
# ----------------------------------------------------------------------

# Removing the driver package, we simply orphan any related DSNs
%preun
myodbc-installer -r -d -n "MySQL ODBC 5.3 Unicode Driver"
myodbc-installer -r -d -n "MySQL ODBC 5.3 ANSI Driver"

# Removing the setup RPM, downgrade the registration
%if 0%{?odbc_gui}
%preun setup
if [ "$1" = 0 ]; then
    if [ -x %{_bindir}/myodbc-installer ]; then
        %{_bindir}/myodbc-installer -r -d -n "MySQL ODBC 5.3 Unicode Driver" > /dev/null 2>&1 || :
        %{_bindir}/myodbc-installer -r -d -n "MySQL ODBC 5.3 ANSI Driver"    > /dev/null 2>&1 || :
        %{_bindir}/myodbc-installer -a -d -n "MySQL ODBC 5.3 Unicode Driver" -t "DRIVER=%{_libdir}/libmyodbc5w.so" > /dev/null 2>&1 || :
        %{_bindir}/myodbc-installer -a -d -n "MySQL ODBC 5.3 ANSI Driver"    -t "DRIVER=%{_libdir}/libmyodbc5a.so" > /dev/null 2>&1 || :
    fi
fi
%endif

##############################################################################
#
#  Listing of files to be in the package
#
##############################################################################

%files
%defattr(-, root, root, -)
%{_bindir}/myodbc-installer
%{_libdir}/libmyodbc5w.so
%{_libdir}/libmyodbc5a.so
%doc %{license_files}
%doc ChangeLog README README.debug INSTALL Licenses_for_Third-Party_Components.txt

%if 0%{?odbc_gui}
%files setup
%defattr(-, root, root, -)
%{_libdir}/libmyodbc5S.so
%endif

%files test
%attr(-, root, root) %{_datadir}/mysql-connector-odbc/test
%attr(755, root, root) %{_bindir}/dltest

##############################################################################
