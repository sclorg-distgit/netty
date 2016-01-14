%{?scl:%scl_package netty}
%{!?scl:%global pkg_name %{name}}

# Use java common's requires/provides generator
%{?java_common_find_provides_and_requires}

# Exclude generation of osgi() style provides, since they are not
# SCL-namespaced and may conflict with base RHEL packages.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1045449
%global __provides_exclude ^osgi(.*)$

Name:           %{?scl_prefix}netty
Version:        3.6.3
# Release should be higher than el6 builds. Use convention
# 60.X where X is an increasing int. 60 for rhel-6. We use
# 70.X for rhel-7. For some reason we cannot rely on the
# dist tag.
Release:        70.4%{?dist}
Summary:        An asynchronous event-driven network application framework and tools for Java

Group:          Development/Libraries
License:        ASL 2.0
URL:            https://netty.io/
Source0:        http://%{pkg_name}.googlecode.com/files/%{pkg_name}-%{version}.Final-dist.tar.bz2
Patch0:         %{pkg_name}-port-to-jzlib-1.1.0.patch
Patch1:         %{pkg_name}-fix-marshaller-logger.patch

BuildArch:      noarch

BuildRequires:  %{?scl_prefix_java_common}maven-local
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
%{?scl:Requires: %scl_runtime}

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
%{?scl:Requires: %scl_runtime}

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
* Mon Jan 19 2015 Severin Gehwolf <sgehwolf@redhat.com> - 3.6.3-70.4
- Manually require maven30-ant-contrib since maven-antrun-plugin
  needs it.

* Mon Jan 19 2015 Severin Gehwolf <sgehwolf@redhat.com> - 3.6.3-70.3
- Use java common's BRs since they are no longer in maven's collection.

* Fri Dec 19 2014 Severin Gehwolf <sgehwolf@redhat.com> - 3.6.3-70.2
- Build using maven collection.
- Use java common's provides/requires generators.

* Mon Jun 23 2014 Severin Gehwolf <sgehwolf@redhat.com> - 3.6.3-70.1
- Add requires for thermostat1-runtime package.

* Fri Dec 20 2013 Severin Gehwolf <sgehwolf@redhat.com> - 3.6.3-6
- Don't generate osgi() style provides.
- Fix bogus changelog date.
- Resolves: RHBZ#1045449.

* Wed Nov 27 2013 Severin Gehwolf <sgehwolf@redhat.com> - 3.6.3-5
- Properly enable SCL.

* Tue Nov 12 2013 Severin Gehwolf <sgehwolf@redhat.com> - 3.6.3-4
- SCL-ize package

* Wed Feb 27 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.3-3
- Set scope of optional compile dependencies to 'provided'

* Wed Feb 27 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.3-2
- Drop dependency on OSGi
- Resolves: rhbz#916139

* Mon Feb 25 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.3-1
- Update to upstream version 3.6.3

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 3.6.2-2
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Wed Jan 16 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.2-1
- Update to upstream version 3.6.2

* Tue Jan 15 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.1-1
- Update to upstream version 3.6.1

* Thu Dec 13 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.11-2
- Use system jzlib instead of bundled jzlib
- Resolves: rhbz#878391

* Mon Dec  3 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.11-1
- Update to upstream version 3.5.11

* Mon Nov 12 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.10-1
- Update to upstream version 3.5.10

* Thu Oct 25 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.9-1
- Update to upstream version 3.5.9

* Fri Oct  5 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.8-1
- Update to upstream version 3.5.8

* Fri Sep  7 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.7-1
- Update to upstream version 3.5.7

* Mon Sep  3 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.6-1
- Update to upstream version 3.5.6

* Thu Aug 23 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.5-1
- Update to upstream version 3.5.5

* Wed Aug 15 2012 Tomas Rohovsky <trohovsk@redhat.com> - 3.5.4-1
- Update to upstream version 3.5.4

* Tue Jul 24 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.3-1
- Update to upstream version 3.5.3

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul 16 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.2-2
- Add additional depmap for org.jboss.netty:netty
- Fixes #840301

* Thu Jul 12 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.5.2-1
- Update to upstream version 3.5.2
- Convert patches to POM macros
- Enable jboss-logging

* Fri May 18 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.4-4
- Add enforcer-plugin to BR

* Wed Apr 18 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.4-3
- Remove eclipse plugin from BuildRequires

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Dec  5 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.4-1
- Update to latest upstream version

* Mon Jul 4 2011 Alexander Kurtakov <akurtako@redhat.com> 3.2.3-4
- Fix FTBFS.
- Adapt to current guidelines.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 17 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.3-2
- Use maven 3 to build
- Drop ant-contrib depmap (no longer needed)

* Thu Jan 13 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.2.3-1
- Initial version of the package
