%define file_permissions_user jupyterhub
%define file_permissions_group jupyterhub

%define app_prefix opt/jupyterhub

%define venv_cmd virtualenv -q --python=python3.4
%define venv_name venv

%define venv_install_dir %{app_prefix}/%{venv_name}
%define venv_buildroot_dir %{buildroot}/%{venv_install_dir}
%define venv_bin %{venv_buildroot_dir}/bin

%define venv_python %{venv_bin}/python
%define venv_pip %{venv_python} %{venv_bin}/pip install 

%define __prelink_undo_cmd %{nil}

# Globals
%global __requires_exclude ^/%{venv_buildroot_dir}/bin/python$
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
#%define __os_install_post    \
#    /usr/lib/rpm/redhat/brp-compress \
#    %{!?__debug_package:/usr/lib/rpm/redhat/brp-strip %{__strip}} \
#    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} \
#    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} \
#    %{!?__jar_repack:/usr/lib/rpm/redhat/brp-java-repack-jars} \
#%{nil}

# Tags
Name: venv-jupyterhub
Version: 1.4
Release: 1
Summary: JupyterHub
URL: https://jupyterhub.readthedocs.io
Packager: J. M. Becker <j.becker@amtrustgroup.com>
Distribution: el7
Group: Application/System
License: GPLv3
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
#AutoReq: No
#AutoProv: No
Source0: %{name}.service
Source1: %{name}.sh

%{?systemd_requires}
BuildRequires: systemd

# Blocks
%files
%defattr(-,%{file_permissions_user},%{file_permissions_group},-)
/%{app_prefix}
%{_unitdir}/%{name}.service

%clean
rm -rf %{buildroot}

%install
%{venv_cmd} %{venv_buildroot_dir}
%{venv_pip} jupyterhub jupyter nodeenv git+https://github.com/jupyterhub/systemdspawner.git@master

. %{venv_buildroot_dir}/bin/activate
nodeenv -p
npm install -g configurable-http-proxy
deactivate

sed -i "s:%{venv_buildroot_dir}:/%{venv_install_dir}:" %{venv_buildroot_dir}/bin/shim %{venv_buildroot_dir}/bin/activate
find %{venv_buildroot_dir}/lib/node_modules -type f -name 'package.json' | xargs sed -i "s:%{venv_buildroot_dir}:/%{venv_install_dir}:"


# RECORD files are used by wheels for checksum. They contain path names which
# match the buildroot and must be removed or the package will fail to build.
find %{buildroot} -name "RECORD" -exec rm -rf {} \;

# Change the virtualenv path to the target installation direcotry.
venvctrl-relocate --source=%{venv_buildroot_dir} --destination=/%{venv_install_dir}

# Strip native modules as they contain buildroot paths in their debug information
#find %{venv_buildroot_dir}/lib -type f -name "*.so" | xargs -r strip

install -p -D -m 755 %{SOURCE1} %{buildroot}/%{app_prefix}/conf/%{name}.sh
install -p -D -m 644 %{SOURCE0} %{buildroot}%{_unitdir}/%{name}.service

%prep
rm -rf %{buildroot}/*
mkdir -p %{buildroot}/%{venv_install_dir}

%pre
getent group jupyterhub >/dev/null || groupadd -f -g 4781 -r jupyterhub
if ! getent passwd jupyterhub >/dev/null ; then
    if ! getent passwd 4781 >/dev/null ; then
      useradd -r -u 4781 -g jupyterhub -m -d /var/lib/jupyterhub -s /sbin/nologin -c "jupyter notebook server" jupyterhub
    else
      useradd -r -g jupyterhub -m -d /var/lib/jupyterhub -s /sbin/nologin -c "jupyter notebook  server" jupyterhub
    fi
    chown -R jupyterhub:jupyterhub /var/lib/jupyterhub
    chmod 0750 /var/lib/jupyterhub
fi
exit 0

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service



%description
virtual environment containing jupyterhub

