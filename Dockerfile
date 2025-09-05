# This creates the image only for the system that creates the forest problems.

# Maybe swap out for something more lightweight!
FROM ubuntu:latest AS builder

WORKDIR /app/wd/

COPY . .

USER root

ENV SOLVER_BINARIES_DIR="/opt/solver_binaries"
ENV PATH="${SOLVER_BINARIES_DIR}/ampl.linux-intel64:$PATH"

RUN apt-get update && \
    apt-get install -y \
    r-base-core python3 \
    python3-venv git \
    curl build-essential \
    python3-dev libtirpc-dev wget && \
    apt-get clean all && mkdir -p $SOLVER_BINARIES_DIR && \
    wget -qO- https://github.com/industrial-optimization-group/DESDEO/releases/download/supplementary/solver_binaries.tgz | tar -xz -C $SOLVER_BINARIES_DIR && \
    ./docker-setup.sh

FROM ubuntu:latest AS runner

WORKDIR /app/wd

COPY --from=builder /opt /opt
COPY . .

RUN apt-get update && \
    apt-get install -y python3 r-base-core && apt-get clean all && \
    chmod 777 /app/

ENV SOLVER_BINARIES_DIR="/opt/solver_binaries"
ENV PATH="${SOLVER_BINARIES_DIR}/ampl.linux-intel64:$PATH"
ENV PIPELINE_OUTPUT="/app/output"

USER 1000

CMD ["./docker-run.sh"]

EXPOSE 8000 5174