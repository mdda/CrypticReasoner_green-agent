FROM ghcr.io/astral-sh/uv:python3.13-bookworm

RUN adduser agent 
#RUN groupadd -r agent && useradd -r -g agent agent

USER agent
WORKDIR /home/agent

# Will have root permissions...
COPY pyproject.toml uv.lock README.md ./
RUN id -a  
##10 0.114 uid=1000(agent) gid=1000(agent) groups=1000(agent),100(users)
##10 DONE 0.1s

RUN ls -la
#11 [stage-0  6/13] RUN ls -la
#11 0.130 total 104
#11 0.130 drwx------ 1 agent agent  4096 Jan 11 09:59 .
#11 0.130 drwxr-xr-x 1 root  root   4096 Jan 11 09:59 ..
#11 0.130 -rw-r--r-- 1 agent agent   220 Jan 11 09:59 .bash_logout
#11 0.130 -rw-r--r-- 1 agent agent  3526 Jan 11 09:59 .bashrc
#11 0.130 -rw-r--r-- 1 agent agent   807 Jan 11 09:59 .profile
#11 0.130 -rw-r--r-- 1 root  root   3267 Jan 11 09:59 README.md
#11 0.130 -rw-r--r-- 1 root  root    564 Jan 11 09:59 pyproject.toml
#11 0.130 -rw-r--r-- 1 root  root  71225 Jan 11 09:59 uv.lock
#11 DONE 0.1s

RUN \
    --mount=type=cache,target=/home/agent/.cache/uv,uid=1000 \
    uv sync --locked

# User 'agent' permissions
# Copy files and change ownership to 'myuser:myuser' immediately
COPY --chown=agent:agent src src

# Run setup script (this is ugly...)
WORKDIR /home/agent/src

RUN id -a  
## uid=1000(agent) gid=1000(agent) groups=1000(agent),100(users)
RUN ls -l
##16 0.132 total 24
##16 0.132 -rw-r--r-- 1 agent agent 3368 Jan 11 09:59 agent.py
##16 0.132 -rw-r--r-- 1 agent agent 1983 Jan 11 09:59 executor.py
##16 0.132 -rw-r--r-- 1 agent agent 3826 Jan 11 09:59 messenger.py
##16 0.132 -rw-r--r-- 1 agent agent 2221 Jan 11 09:59 server.py
##16 0.132 -rw-r--r-- 1 agent agent  449 Jan 11 09:59 setup-resize-embeddings.py
##16 0.132 -rwxr-xr-x 1 agent agent 2071 Jan 11 09:59 setup.sh
RUN ./setup.sh
WORKDIR /home/agent

ENTRYPOINT ["uv", "run", "src/server.py"]
CMD ["--host", "0.0.0.0"]
EXPOSE 9009
