%{?scl:%scl_package netty}
%{!?scl:%global pkg_name %{name}}

# Disable generation of debuginfo package
%global debug_package %{nil}
%global namedreltag .Final
%global namedversion %{version}%{?namedreltag}

Name:           %{?scl_prefix}netty
Version:        4.0.42
Release:        5.1%{?dist}
Summary:        An asynchronous event-driven network application framework and tools for Java
License:        ASL 2.0
URL:            https://netty.io/
Source0:        https://github.com/netty/netty/archive/netty-%{namedversion}.tar.gz
Patch0:         0001-Remove-OpenSSL-parts-depending-on-tcnative.patch
Patch1:         0002-Remove-NPN-ALPN.patch
Patch2:         fix-sendmmsg-detection.patch

BuildRequires:  %{?scl_prefix_maven}maven-local
BuildRequires:  %{?scl_prefix_maven}mvn(ant-contrib:ant-contrib)
BuildRequires:  %{?scl_prefix_maven}mvn(com.jcraft:jzlib)
BuildRequires:  %{?scl_prefix_maven}mvn(commons-logging:commons-logging)
BuildRequires:  %{?scl_prefix_maven}mvn(log4j:log4j:1.2.17)
BuildRequires:  %{?scl_prefix_maven}mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires:  %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-dependency-plugin)
BuildRequires:  %{?scl_prefix_maven}mvn(org.codehaus.mojo:build-helper-maven-plugin)
BuildRequires:  %{?scl_prefix_maven}mvn(org.fusesource.hawtjni:maven-hawtjni-plugin)
BuildRequires:  %{?scl_prefix_maven}mvn(org.javassist:javassist)
BuildRequires:  %{?scl_prefix_maven}mvn(org.slf4j:slf4j-api)
BuildRequires:  %{?scl_prefix_maven}mvn(org.sonatype.oss:oss-parent:pom:)

BuildRequires:  %{?scl_prefix}mvn(kr.motd.maven:os-maven-plugin)
BuildRequires:  %{?scl_prefix}mvn(org.apache.logging.log4j:log4j-api)
BuildRequires:  %{?scl_prefix}mvn(org.jctools:jctools-core)

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
Summary:   API documentation for %{pkg_name}

%description javadoc
%{summary}.

%prep
%setup -q -n netty-netty-%{namedversion}

%patch0 -p1
%patch1 -p1
%patch2 -p1

# Missing Mavenized rxtx
%pom_disable_module "transport-rxtx"
%pom_remove_dep ":netty-transport-rxtx" all
# Missing com.barchart.udt:barchart-udt-bundle:jar:2.3.0
%pom_disable_module "transport-udt"
%pom_remove_dep ":netty-transport-udt" all
%pom_remove_dep ":netty-build" all
# Not needed
%pom_disable_module "example"
%pom_remove_dep ":netty-example" all
%pom_disable_module "testsuite"
%pom_disable_module "testsuite-osgi"
%pom_disable_module "tarball"
%pom_disable_module "microbench"
%pom_remove_plugin :maven-checkstyle-plugin
%pom_remove_plugin :animal-sniffer-maven-plugin
%pom_remove_plugin :maven-enforcer-plugin
%pom_remove_plugin :maven-antrun-plugin
%pom_remove_plugin :maven-dependency-plugin
%pom_remove_plugin :maven-shade-plugin
%pom_remove_plugin :maven-shade-plugin common
%pom_remove_plugin :xml-maven-plugin
%pom_remove_plugin -r :maven-release-plugin
%pom_remove_plugin -r :maven-clean-plugin
%pom_remove_plugin -r :maven-source-plugin
%pom_remove_plugin -r :maven-deploy-plugin
%pom_remove_plugin -r :maven-jxr-plugin
%pom_remove_plugin -r :maven-javadoc-plugin
# Optional things we don't ship
%pom_remove_dep ":\${tcnative.artifactId}"
%pom_remove_dep ":\${tcnative.artifactId}" handler
%pom_remove_dep "org.eclipse.jetty.npn:npn-api"
%pom_remove_dep "org.eclipse.jetty.npn:npn-api" handler
%pom_remove_dep "org.eclipse.jetty.alpn:alpn-api"
%pom_remove_dep "org.eclipse.jetty.alpn:alpn-api" handler

%pom_remove_dep -r "com.google.protobuf:protobuf-java"
rm codec/src/main/java/io/netty/handler/codec/protobuf/*
%pom_remove_dep -r "org.jboss.marshalling:jboss-marshalling"
rm codec/src/main/java/io/netty/handler/codec/marshalling/*
%pom_remove_dep -r org.bouncycastle
rm handler/src/main/java/io/netty/handler/ssl/util/BouncyCastleSelfSignedCertGenerator.java
sed -i '/BouncyCastleSelfSignedCertGenerator/s/.*/throw new UnsupportedOperationException();/' \
    handler/src/main/java/io/netty/handler/ssl/util/SelfSignedCertificate.java

sed -i 's|taskdef|taskdef classpathref="maven.plugin.classpath"|' all/pom.xml

%pom_xpath_inject "pom:plugins/pom:plugin[pom:artifactId = 'maven-antrun-plugin']" '<dependencies><dependency><groupId>ant-contrib</groupId><artifactId>ant-contrib</artifactId><version>1.0b3</version></dependency></dependencies>' all/pom.xml
%pom_xpath_inject "pom:execution[pom:id = 'build-native-lib']/pom:configuration" '<verbose>true</verbose>' transport-native-epoll/pom.xml

# Upstream has jctools bundled.
%pom_xpath_remove "pom:build/pom:plugins/pom:plugin[pom:artifactId = 'maven-bundle-plugin']/pom:executions/pom:execution[pom:id = 'generate-manifest']/pom:configuration/pom:instructions/pom:Import-Package" common/pom.xml

# Tell xmvn to install attached artifact, which it does not
# do by default. In this case install all attached artifacts with
# the linux classifier.
%mvn_package ":::linux*:"

%build
export CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_LD_FLAGS"
%mvn_build -f

%install
%mvn_install

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Fri Jun 23 2017 Michael Simacek <msimacek@redhat.com> - 4.0.42-5.1
- Package import and sclization

* Wed Mar 29 2017 Michael Simacek <msimacek@redhat.com> - 4.0.42-5
- Keep Import-Package default value

* Thu Mar 16 2017 Michael Simacek <msimacek@redhat.com> - 4.0.42-4
- Remove maven-javadoc-plugin from POM

* Wed Mar 15 2017 Michael Simacek <msimacek@redhat.com> - 4.0.42-3
- Add jp_minimal conditional

* Mon Feb 06 2017 Michael Simacek <msimacek@redhat.com> - 4.0.42-2
- Remove useless plugins

* Thu Oct 20 2016 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.42-1
- Remove old netty4 provides/obsoletes.

* Thu Oct 20 2016 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.42-1
- Update to upstream 4.0.42 release.
- Resolves RHBZ#1380921

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.28-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.28-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 20 2015 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.28-1
- Update to upstream 4.0.28 release.
- Fixes CVE-2015-2156 (HttpOnly cookie bypass).
- Resolves RHBZ#1111502

* Wed May 20 2015 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.27-1
- Update to upstream 4.0.27 release.

* Wed Apr 01 2015 Severin Gehwolf <sgehwolf@redhat.com> - 4.0.19-3
- Drop mvn(org.easymock:easymockclassextension) BR.
  Resolves: RHBZ#1207991

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jun  9 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 4.0.19-1
- Update to upstream version 4.0.19
- Convert to arch-specific package

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.14-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 04 2014 Stanislav Ochotnicky <sochotnicky@redhat.com> - 4.0.14-4
- Use Requires: java-headless rebuild (#1067528)

* Mon Jan 13 2014 Marek Goldmann <mgoldman@redhat.com> - 4.0.14-3
- Enable netty-all.jar artifact

* Mon Jan 13 2014 Marek Goldmann <mgoldman@redhat.com> - 4.0.14-2
- Bump the release, so Obsoletes work properly

* Mon Dec 30 2013 Marek Goldmann <mgoldman@redhat.com> - 4.0.14-1
- Upstream release 4.0.14.Final

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu May 16 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.6-1
- Update to upstream version 3.6.6

* Wed Apr 10 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.5-1
- Update to upstream version 3.6.5

* Mon Apr  8 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.6.4-1
- Update to upstream version 3.6.4

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
