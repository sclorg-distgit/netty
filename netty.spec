%{?scl:%scl_package netty}
%{!?scl:%global pkg_name %{name}}

# Use java common's requires/provides generator
%{?java_common_find_provides_and_requires}

%if 0%{?rhel}

%if 0%{?rhel} <= 6
  # EL 6
  %global custom_release 60
%else
  # EL 7
  %global custom_release 70
%endif

%else

%global custom_release 1

%endif

Name:           %{?scl_prefix}netty
Version:        3.6.3
Release:        %{custom_release}.2%{?dist}
Summary:        An asynchronous event-driven network application framework and tools for Java

Group:          Development/Libraries
License:        ASL 2.0
URL:            https://netty.io/
Source0:        http://%{pkg_name}.googlecode.com/files/%{pkg_name}-%{version}.Final-dist.tar.bz2
Patch0:         %{pkg_name}-port-to-jzlib-1.1.0.patch
Patch1:         %{pkg_name}-fix-marshaller-logger.patch

BuildArch:      noarch

BuildRequires:  %{?scl_prefix_maven}maven-local
BuildRequires:  %{?scl_prefix_maven}maven-antrun-plugin
# maven-antrun-plugin has ant-contrib as dependency, but fails
# to have this BR for it. We work around it by requiring it
# manually.
BuildRequires:  %{?scl_prefix_maven}ant-contrib
BuildRequires:  %{?scl_prefix_maven}maven-assembly-plugin
BuildRequires:  %{?scl_prefix_maven}maven-compiler-plugin
BuildRequires:  %{?scl_prefix_maven}maven-enforcer-plugin
BuildRequires:  %{?scl_prefix_maven}maven-javadoc-plugin
BuildRequires:  %{?scl_prefix_maven}maven-plugin-bundle
BuildRequires:  %{?scl_prefix_maven}maven-resources-plugin
BuildRequires:  %{?scl_prefix_maven}maven-source-plugin
BuildRequires:  %{?scl_prefix_maven}maven-surefire-plugin
BuildRequires:  %{?scl_prefix_java_common}ant

BuildRequires:  %{?scl_prefix_maven}felix-osgi-compendium
BuildRequires:  %{?scl_prefix_maven}felix-osgi-core
BuildRequires:  %{?scl_prefix}protobuf-java
BuildRequires:  %{?scl_prefix_java_common}slf4j
BuildRequires:  %{?scl_prefix_maven}sonatype-oss-parent
BuildRequires:  %{?scl_prefix_java_common}tomcat-servlet-3.0-api

%description
Netty is a NIO client server framework which enables quick and easy
development of network applications such as protocol servers and
clients. It greatly simplifies and streamlines network programming
such as TCP and UDP socket server.

'Quick and easy' doesn't mean that a resulting application will suffer
from a maintainability or a performance issue. Netty has been designed
carefully with the experiences earned from the implementation of a lot
of protocols such as FTP, SMTP, HTTP, and various binary and
text-based legacy protocols. As a result, Netty has succeeded to find
a way to achieve ease of development, performance, stability, and
flexibility without a compromise.


%package javadoc
Summary:   API documentation for %{name}
Group:     Documentation

%description javadoc
%{summary}.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%setup -q -n %{pkg_name}-%{version}.Final
# just to be sure, but not used anyway
rm -rf jar doc license

%pom_remove_plugin :maven-jxr-plugin
%pom_remove_plugin :maven-checkstyle-plugin
%pom_remove_plugin org.eclipse.m2e:lifecycle-mapping
%pom_remove_dep javax.activation:activation

# Remove optional deps
%pom_remove_dep org.jboss.logging:jboss-logging-spi
%pom_remove_dep org.jboss.marshalling:jboss-marshalling

%pom_remove_plugin :animal-sniffer-maven-plugin
%pom_xpath_remove "pom:execution[pom:id[text()='remove-examples']]"
%pom_xpath_remove "pom:plugin[pom:artifactId[text()='maven-javadoc-plugin']]/pom:configuration"
# Set scope of optional compile dependencies to 'provided'
%pom_xpath_set "pom:dependency[pom:scope[text()='compile']
	       and pom:optional[text()='true']]/pom:scope" provided

# Remove bundled jzlib and use system jzlib
rm -rf src/main/java/org/jboss/netty/util/internal/jzlib
%pom_add_dep com.jcraft:jzlib
sed -i s/org.jboss.netty.util.internal.jzlib/com.jcraft.jzlib/ \
    $(find src/main/java/org/jboss/netty/handler/codec -name \*.java | sort -u)
%patch0 -p1
%patch1 -p1
%{?scl:EOF}

%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_alias : org.jboss.netty:
%mvn_file  : %{pkg_name}
# skipping tests because we don't have easymockclassextension
%mvn_build -f
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install
%{?scl:EOF}

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Tue Jan 17 2017 Jie Kang <jkang@redhat.com> - 3.6.3-2
- Rebuild for RHSCL 2.4.

* Fri Jun 24 2016 Severin Gehwolf <sgehwolf@redhat.com> - 3.6.3-1
- Initial package.
