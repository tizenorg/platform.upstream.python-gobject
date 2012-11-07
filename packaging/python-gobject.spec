%define local_py_requires %{py_requires}
%define local_py_sitedir  %{py_sitedir}

Name:           python-gobject
Version:        2.28.6
Release:        6
License:        LGPL-2.1+
%define _name   pygobject
Summary:        Python bindings for GObject
Url:            http://ftp.gnome.org/pub/GNOME/sources/pygobject/
Group:          Development/Libraries/Python
Source:         http://ftp.gnome.org/pub/GNOME/sources/pygobject/2.28/%{_name}-%{version}.tar.bz2
BuildRequires:  fdupes
BuildRequires:  libffi-devel
BuildRequires:  libtool
BuildRequires:  python-devel
BuildRequires:  pkgconfig(glib-2.0)
Provides:       pygobject
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
Pygobjects is an extension module for python that gives you access to
GLib's GObjects.

%package devel
License:        LGPL-2.1+
Summary:        Python bindings for GObject
Group:          Development/Libraries/Python
Requires:       %{name} = %{version}

%description devel
This package contains files required to build wrappers for gobject
addon libraries such as pygtk.

%prep
%setup -q -n %{_name}-%{version}
autoreconf -fi

%build
%configure --disable-static --disable-introspection
make %{?_smp_mflags} V=1

%install
%make_install
rm examples/Makefile*
%fdupes %{buildroot}


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%dir %{local_py_sitedir}/gtk-2.0
%{local_py_sitedir}/gtk-2.0/gio/
%{local_py_sitedir}/glib/
%{local_py_sitedir}/gobject/
%{local_py_sitedir}/gtk-2.0/dsextras.py*
%{local_py_sitedir}/pygtk.*
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root)
%{_includedir}/pygtk-2.0/
%{_libdir}/*.so
%{_libdir}/pkgconfig/pygobject-2.0.pc
## codegen
%{_bindir}/pygobject-codegen-2.0
# we explicitly list the directories here to be sure we don't include something
# that should live in the main package
%dir %{_datadir}/%{_name}
%dir %{_datadir}/%{_name}/2.0
%{_datadir}/%{_name}/2.0/codegen/
%{_datadir}/%{_name}/2.0/defs/
%{_datadir}/%{_name}/xsl/
## doc: we need the files there since building API docs for other python
## bindings require some files from here
# Own these repositories to not depend on gtk-doc while building:
%dir %{_datadir}/gtk-doc
%dir %{_datadir}/gtk-doc/html
%{_datadir}/gtk-doc/html/pygobject/

%changelog
