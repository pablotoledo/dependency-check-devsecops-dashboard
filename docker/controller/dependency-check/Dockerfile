# https://github.com/jeremylong/DependencyCheck
#docker build --build-arg NVD_API_KEY=$NVD_API_KEY -t dpcheck .
FROM openjdk:8-jdk

# Defining environment variables for Dependency-Check
ENV GITHUB_URL="https://github.com/pablotoledo/starting-with-angular.git"
ENV GITHUB_REPO_NAME="sample_repo"
ARG NVD_API_KEY
ENV NVD_API_KEY=${NVD_API_KEY}

# Installing git
RUN apt-get update && \
    apt-get install -y git

# Installing nodejs
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - && \
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
RUN mkdir -p $DC_HOME/temp && \
    VERSION=$(curl -s https://jeremylong.github.io/DependencyCheck/current.txt) && \
    wget -qO dependency-check.zip "https://github.com/jeremylong/DependencyCheck/releases/download/v$VERSION/dependency-check-$VERSION-release.zip" && \
    unzip dependency-check.zip -d $DC_HOME/temp && \
    mv $DC_HOME/temp/dependency-check/* $DC_HOME/ && \
    rm -r $DC_HOME/temp && \
    rm dependency-check.zip

RUN ln -s $DC_HOME/bin/dependency-check.sh /usr/bin/dependency-check
RUN dependency-check --updateonly --nvdApiKey $NVD_API_KEY --nvdApiDelay 20000

# Create a workspace directory
WORKDIR /workspace

# Copy the start.sh script into the workspace directory
COPY start.sh /workspace/start.sh
RUN chmod +x /workspace/start.sh

# Command to run the start.sh script
CMD ["/workspace/start.sh"]