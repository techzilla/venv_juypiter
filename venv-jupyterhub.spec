%define file_permissions_user root
%define file_permissions_group root

%define venv_cmd virtualenv -q --python=python3.4
%define venv_name venv
%define venv_install_dir opt/jupyterhub/%{venv_name}
%define venv_dir %{buildroot}/%{venv_install_dir}
%define venv_bin %{venv_dir}/bin
%define venv_python %{venv_bin}/python
%define venv_pip %{venv_python} %{venv_bin}/pip install 

%define __prelink_undo_cmd %{nil}

# Globals
%global __requires_exclude ^/opt/jupyterhub/venv/bin/python$
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
BuildRoot: %(mktemp -ud %{_tmppath}/%{Name}-%{version}-%{release}-XXXXXX)
#Source0: /home/jbecker/jupyterhub
#AutoReq: No
#AutoProv: No

# Blocks
%files
%defattr(-,%{file_permissions_user},%{file_permissions_group},-)
/%{venv_install_dir}

%clean
rm -rf %{buildroot}

%install
%{venv_cmd} %{venv_dir}
%{venv_pip} jupyterhub jupyter nodeenv

. %{venv_dir}/bin/activate
nodeenv -p
npm install -g configurable-http-proxy
deactivate

sed -i "s:%{venv_dir}:/%{venv_install_dir}:" %{venv_dir}/bin/shim %{venv_dir}/bin/activate
find %{venv_dir}/lib/node_modules -type f -name 'package.json' | xargs sed -i "s:%{venv_dir}:/%{venv_install_dir}:"


# RECORD files are used by wheels for checksum. They contain path names which
# match the buildroot and must be removed or the package will fail to build.
find %{buildroot} -name "RECORD" -exec rm -rf {} \;

# Change the virtualenv path to the target installation direcotry.
venvctrl-relocate --source=%{venv_dir} --destination=/%{venv_install_dir}

# Strip native modules as they contain buildroot paths in their debug information
#find %{venv_dir}/lib -type f -name "*.so" | xargs -r strip

%post
echo post step

%prep
rm -rf %{buildroot}/*
mkdir -p %{buildroot}/%{venv_install_dir}

%description
python virtual environment containing
jupyterhub and jupyter

