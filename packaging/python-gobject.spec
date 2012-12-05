%define local_py_requires %{py_requires}
%define local_py_sitedir  %{py_sitedir}
%define local_py_suffix   %{nil}
%define local_lib_ver     0

Name:           python-gobject
%define _name   pygobject
Summary:        Python bindings for GObject
License:        LGPL-2.1+
Group:          Development/Libraries/Python
Version:        3.4.0
Release:        2.1
Url:            http://ftp.gnome.org/pub/GNOME/sources/pygobject/
Source:         http://download.gnome.org/sources/pygobject/3.4/%{_name}-%{version}.tar.xz
BuildRequires:  fdupes
BuildRequires:  glib2-devel >= 2.31.0
BuildRequires:  gobject-introspection-devel >= 1.33.14
BuildRequires:  libffi-devel
BuildRequires:  python-cairo-devel
BuildRequires:  python-devel
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-gobject)
%{local_py_requires}

%description
Pygobjects is an extension module for python that gives you access to
GLib's GObjects.

%package cairo
Summary:        Python bindings for GObject -- Cairo bindings
Group:          Development/Libraries/Python
Requires:       %{name} = %{version}

%description cairo
Pygobjects is an extension module for python that gives you access to
GLib's GObjects.

This package contains the Python Cairo bindings for GObject.

%package pygtkcompat
Summary:        Python bindings for GObject -- PyGTK Backwards Compatibility
Group:          Development/Libraries/Python
Requires:       %{name} = %{version}

%description pygtkcompat
Pygobjects is an extension module for python that gives you access to
GLib's GObjects.

This package contains a module providing backwards compatibility to
pygtk.

%package -n libpyglib-gi-python
Summary:        Python Gobject Introspeciton binding
Group:          System/Libraries

%description -n libpyglib-gi-python
Pygobjects is an extension module for python that gives you access to
GLib's GObjects.

The bindings are handled by gobject-introspection libraries.

%package devel
Summary:        Python bindings for GObject
Group:          Development/Libraries/Python
Requires:       %{name} = %{version}
Requires:       libpyglib-gi-python = %{version}

%description devel
This package contains files required to build wrappers for gobject
addon libraries such as pygtk.

%prep
%setup -q -n %{_name}-%{version}

%build
%configure
make %{?jobs:-j%jobs} V=1

%install
%make_install
rm examples/Makefile*
%fdupes $RPM_BUILD_ROOT

%post -n libpyglib-gi-python -p /sbin/ldconfig

%postun -n libpyglib-gi-python -p /sbin/ldconfig

%files
%defattr(-,root,root)
%{local_py_sitedir}/gi/
# Lives in cairo subpackage
%exclude %{local_py_sitedir}/gi/_gi_cairo.so
# Lives in pygtkcompat subpackage
%exclude %{local_py_sitedir}/gi/pygtkcompat.py

%files -n libpyglib-gi-python
%defattr(-, root, root)
%{_libdir}/libpyglib-gi-2.0-python%{local_py_suffix}.so.0*

%files cairo
%defattr(-,root,root)
%{local_py_sitedir}/gi/_gi_cairo.so

%files pygtkcompat
%defattr(-,root,root)
%{local_py_sitedir}/gi/pygtkcompat.py

%files devel
%defattr(-,root,root)
%{_includedir}/pygobject-3.0/
%{_libdir}/*.so
%{_libdir}/pkgconfig/pygobject-3.0.pc
