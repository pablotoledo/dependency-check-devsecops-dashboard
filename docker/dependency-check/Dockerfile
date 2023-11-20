# https://github.com/jeremylong/DependencyCheck
FROM openjdk:8-jdk

# Installing git
RUN apt-get update && \
    apt-get install -y git

# Installing nodejs
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs

# Installing Yarn
RUN npm install -g yarn

# Installing Maven
RUN apt-get update && \
    apt-get install -y maven

# Installing Gradle
RUN wget https://services.gradle.org/distributions/gradle-6.7-bin.zip -P /tmp && \
    unzip -d /opt/gradle /tmp/gradle-*.zip && \
    ln -s /opt/gradle/gradle-6.7/bin/gradle /usr/bin/gradle

# Installing pip para Python
RUN apt-get install -y python3-pip

# Removing cache
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Defining environment variables
ENV DC_HOME=/usr/share/dependency-check
ENV PATH="$DC_HOME/bin:$PATH"

# Creating a directory for Dependency-Check and downloading the latest version
RUN mkdir -p $DC_HOME && \
    VERSION=$(curl -s https://jeremylong.github.io/DependencyCheck/current.txt) && \
    wget -qO- "https://github.com/jeremylong/DependencyCheck/releases/download/v$VERSION/dependency-check-$VERSION-release.zip" -O dependency-check.zip && \
    unzip dependency-check.zip -d $DC_HOME && \
    rm dependency-check.zip


