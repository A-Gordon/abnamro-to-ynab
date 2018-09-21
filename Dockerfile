FROM python:2.7

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update \
&& apt-get install -y git \
    supervisor \
    cron \
    google-chrome-stable \
    unzip \
    vim

RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/2.38/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
ENV DISPLAY=:99

# # Ruby 2.4.0
RUN git clone git://github.com/rbenv/rbenv.git /usr/local/rbenv \
&&  git clone git://github.com/rbenv/ruby-build.git /usr/local/rbenv/plugins/ruby-build \
&&  git clone git://github.com/jf/rbenv-gemset.git /usr/local/rbenv/plugins/rbenv-gemset \
&&  /usr/local/rbenv/plugins/ruby-build/install.sh
ENV PATH /usr/local/rbenv/bin:$PATH
ENV RBENV_ROOT /usr/local/rbenv

RUN echo 'export RBENV_ROOT=/usr/local/rbenv' >> /etc/profile.d/rbenv.sh \
&&  echo 'export PATH=/usr/local/rbenv/bin:$PATH' >> /etc/profile.d/rbenv.sh \
&&  echo 'eval "$(rbenv init -)"' >> /etc/profile.d/rbenv.sh

RUN echo 'export RBENV_ROOT=/usr/local/rbenv' >> /root/.bashrc \
&&  echo 'export PATH=/usr/local/rbenv/bin:$PATH' >> /root/.bashrc \
&&  echo 'eval "$(rbenv init -)"' >> /root/.bashrc

ENV CONFIGURE_OPTS --disable-install-doc
ENV PATH /usr/local/rbenv/bin:/usr/local/rbenv/shims:$PATH

ENV RBENV_VERSION 2.4.0
RUN apt-get install -y libreadline-dev

RUN eval "$(rbenv init -)"; rbenv install $RBENV_VERSION \
&&  eval "$(rbenv init -)"; rbenv global $RBENV_VERSION \
&&  eval "$(rbenv init -)"; gem update --system \
&&  eval "$(rbenv init -)"; gem install bundler -f \
&&  rm -rf /tmp/*

RUN gem install bundle \
    bundler \
    rails

ADD supervisord/supervisord.conf /etc/supervisord.conf
ADD supervisord/crond.ini /etc/supervisord.d/crond.ini
ADD cron/crontab /etc/crontab

RUN chmod 0600 /etc/supervisord.conf /etc/supervisord.d/*.ini \
&& /usr/bin/crontab /etc/crontab \
&& touch /var/log/cron.log 

ADD . /src
RUN cd /src; pip install -r requirements.txt
RUN cd /src/fintech-to-ynab; bundle 

CMD ["cron", "-f"]