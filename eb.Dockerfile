# source: https://gitlab.com/cs373-11am-group-6/trailmix/-/blob/dev/backend/eb.Dockerfile
# for use with Elastic Beanstalk deployment

FROM python:3.10-slim
SHELL ["bash", "-c"]
WORKDIR /setup

RUN apt-get update
RUN apt-get install git curl build-essential zlib1g-dev libssl-dev libncurses-dev libffi-dev libsqlite3-dev libreadline-dev libbz2-dev -y

RUN pip install --upgrade pip
RUN pip uninstall -y virtualenv
RUN pip install virtualenv
RUN git clone https://github.com/aws/aws-elastic-beanstalk-cli-setup.git
RUN python ./aws-elastic-beanstalk-cli-setup/scripts/ebcli_installer.py
ENV PATH="~/.ebcli-virtual-env/executables:$PATH"
RUN eb --version

CMD bash