FROM alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc AS asset-stage

WORKDIR /src

COPY /src /src/

RUN test -f /src/index.html && \
    test -f /src/advisory.html && \
    test -f /src/history.html

FROM nginxinc/nginx-unprivileged:1.27-alpine-slim@sha256:ec6b8b1f1bfa594db13e99fc692b9fb816cb7e365927196610f622659de95913 AS runner

LABEL maintainer="user <user@agricloud.internal>"

LABEL description="Unprivileged Nginx reverse proxy & static asset server for AgriCloud-CI"

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=asset-stage --chown=101:101 ./src /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]