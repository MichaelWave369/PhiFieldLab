# D3 experimental container. Base image must be obtained and reviewed separately.
# Never use an unreviewed remote base or assume this image is independently attested.
FROM python:3.11-alpine
LABEL org.phifieldlab.contract="PHIFIELD_D3_CLEANROOM_V1" \
      org.phifieldlab.adapter="SYNTHETIC_QUEUE_V1"
COPY src/phifieldlab/__init__.py /usr/local/lib/python3.11/site-packages/phifieldlab/__init__.py
COPY src/phifieldlab/d2_network_sim.py /usr/local/lib/python3.11/site-packages/phifieldlab/d2_network_sim.py
COPY src/phifieldlab/d2_network_worker.py /usr/local/lib/python3.11/site-packages/phifieldlab/d2_network_worker.py
WORKDIR /tmp
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 65534:65534
ENTRYPOINT ["python", "-I", "-m", "phifieldlab.d2_network_worker"]
