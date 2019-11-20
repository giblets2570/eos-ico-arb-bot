FROM lambci/lambda:build
RUN curl https://raw.githubusercontent.com/apex/apex/master/install.sh | sh
COPY install_python_36_amazon_linux.sh /tmp
RUN cd /tmp && yum install wget -y && chmod u+x install_python_36_amazon_linux.sh && ./install_python_36_amazon_linux.sh && cd -
COPY .aws /root/.aws
ENV ENV=development
WORKDIR /usr/src/app