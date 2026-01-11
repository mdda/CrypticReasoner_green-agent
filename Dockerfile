FROM ghcr.io/astral-sh/uv:python3.13-bookworm

#RUN adduser agent
RUN groupadd -r agent && useradd -r -g agent agent

USER agent
WORKDIR /home/agent

# Will have root permissions...
COPY pyproject.toml uv.lock README.md ./
#RUN id -a  
## uid=1000(agent) gid=1000(agent) groups=1000(agent),100(users)
#RUN ls -l
##13 0.136 total 84
##13 0.136 -rw-r--r-- 1 root root  3267 Jan 11 08:55 README.md
##13 0.136 -rw-r--r-- 1 root root   564 Jan 11 08:55 pyproject.toml
##13 0.136 drwxr-xr-x 2 root root  4096 Jan 11 08:55 src
##13 0.136 -rw-r--r-- 1 root root 71225 Jan 11 08:55 uv.lock

RUN \
    --mount=type=cache,target=/home/agent/.cache/uv,uid=1000 \
    uv sync --locked

# User 'agent' permissions
# Copy files and change ownership to 'myuser:myuser' immediately
COPY --chown=agent:agent src src

RUN id -a  
RUN ls -l

# Run setup script (this is ugly...)
WORKDIR /home/agent/src
RUN ./setup.sh
WORKDIR /home/agent

ENTRYPOINT ["uv", "run", "src/server.py"]
CMD ["--host", "0.0.0.0"]
EXPOSE 9009
