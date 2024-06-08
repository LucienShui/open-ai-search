FROM python:3.10-alpine
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt \
    -i https://mirrors.ustc.edu.cn/pypi/web/simple \
    -i https://pypi.tuna.tsinghua.edu.cn/simple
