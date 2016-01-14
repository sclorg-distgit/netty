%{?scl:%scl_package netty}
%{!?scl:%global pkg_name %{name}}

Name:           %{?scl_prefix}netty
Version:        3.6.3
# Release should be higher than el7 builds. Use convention
# 60.X where X is an increasing int. 60 for rhel-6. We use
# 70.X for rhel-7. For some reason we cannot rely on the
# dist tag.
Release:        60.4%{?dist}
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
BuildRequires:  %{?scl_prefix_maven}maven-assembly-plugin
BuildRequires:  %{?scl_prefix_maven}maven-compiler-plugin
BuildRequires:  %{?scl_prefix_maven}maven-enforcer-plugin
BuildRequires:  %{?scl_prefix_maven}maven-javadoc-plugin
BuildRequires:  %{?scl_prefix_maven}maven-plugin-bundle
BuildRequires:  %{?scl_prefix_maven}maven-resources-plugin
BuildRequires:  %{?scl_prefix_maven}maven-source-plugin
BuildRequires:  %{?scl_prefix_maven}maven-surefire-plugin
BuildRequires:  %{?scl_prefix_maven}ant-contrib
BuildRequires:  %{?scl_prefix_maven}sonatype-oss-parent
BuildRequires:  %{?scl_prefix_java_common}mvn(javax.servlet:servlet-api)
BuildRequires:  %{?scl_prefix_java_common}slf4j

BuildRequires:  %{?scl_prefix_maven}felix-osgi-compendium
BuildRequires:  %{?scl_prefix_maven}felix-osgi-core
BuildRequires:  %{?scl_prefix}protobuf-java

# Require jzlib this way. This would be generated
# automatically by the Java auto-requires generator, but
# since the base RHEL-6 package does not have the suitable
# mvn() provides, work around it this way.
Requires:       jzlib
Requires:       java
%{?scl:Requires: %scl_runtime}
# Manual provides for thermostat package
Provides:       %{?scl_prefix}mvn(org.jboss.netty:netty) = %{version}

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
# Make sure we depend on the scl-runtime package
# for javadoc dir ownership
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
* Tue Jan 20 2015 Severin Gehwolf <sgehwolf@redhat.com> 3.6.3-60.4
- Use java common's libs as BR.

* Wed Dec 17 2014 Severin Gehwolf <sgehwolf@redhat.com> 3.6.3-60.3
- Don't use hard-coded maven collection name.

* Fri Jun 20 2014 Severin Gehwolf <sgehwolf@redhat.com> 3.6.3-60.2
- Add manual mvn()-style provides.

* Wed Jun 18 2014 Severin Gehwolf <sgehwolf@redhat.com> 3.6.3-60.1
- Build using the maven30 collection.

* Wed Nov 27 2013 Severin Gehwolf <sgehwolf@redhat.com> 3.6.3-6
- Properly enable SCL.

* Mon Nov 18 2013 Severin Gehwolf <sgehwolf@redhat.com> 3.6.3-5
- Build using SCL-ized deps.
- Require jzlib from base RHEL-6 and don't use auto-requires
  provides macro.

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

* Thu Aug 15 2012 Tomas Rohovsky <trohovsk@redhat.com> - 3.5.4-1
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
