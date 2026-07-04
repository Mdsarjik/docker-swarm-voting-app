# 🗳️ Docker Swarm Voting App

> A fully containerized, multi-service voting application deployed on **Docker Swarm** — demonstrating service orchestration, overlay networking, load balancing, and fault tolerance across a replicated cluster.

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │             Docker Swarm Cluster             │
                    │                                              │
  [Browser]──5000──►│  vote (x2 replicas)  ──► redis ──► worker  │
                    │                                    │         │
  [Browser]──5001──►│  result (x1 replica) ◄────────── db        │
                    │                                              │
                    │  Networks: frontend (overlay)                │
                    │            backend  (overlay)                │
                    └─────────────────────────────────────────────┘
```

| Service    | Technology      | Role                                        | Replicas |
|------------|-----------------|---------------------------------------------|----------|
| `vote`     | Python / Flask  | Web UI — accepts votes, pushes to Redis     | 2        |
| `result`   | Node.js / EJS   | Web UI — reads from PostgreSQL, shows count | 1        |
| `worker`   | Python          | Consumes Redis queue, writes to PostgreSQL  | 1        |
| `redis`    | Redis 7 Alpine  | Message queue between vote and worker       | 1        |
| `db`       | PostgreSQL 15   | Persistent vote store                       | 1        |

---

## 🚀 Quick Start

### Option A — Docker Swarm (Production mode)

```bash
# 1. Initialise Swarm (skip if already a Swarm node)
docker swarm init

# 2. Deploy the stack
docker stack deploy -c docker-stack.yml voting-app

# 3. Check services
docker service ls

# 4. Watch worker logs
docker service logs -f voting-app_worker
```

| URL | Service |
|-----|---------|
| http://localhost:5000 | 🗳️ Vote page |
| http://localhost:5001 | 📊 Results page (auto-refreshes every 3s) |

### Option B — Docker Compose (Local development)

```bash
# Build and run all services locally
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f worker
```

---

## 📂 Project Structure

```
docker-swarm-voting-app/
├── vote/
│   ├── app.py              # Flask application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── templates/
│       └── index.html      # Vote UI (dark terminal theme)
├── result/
│   ├── server.js           # Node.js Express application
│   ├── package.json
│   ├── Dockerfile
│   └── views/
│       └── index.ejs       # Results UI with live bar chart
├── worker/
│   ├── worker.py           # Redis → PostgreSQL consumer
│   ├── requirements.txt
│   └── Dockerfile
├── docker-stack.yml        # Swarm deployment (production)
├── docker-compose.yml      # Local development
└── README.md
```

---

## ⚙️ How It Works

```
1. User visits :5000 and casts a vote (Cats or Dogs)
2. Flask pushes the vote as JSON onto the Redis 'votes' list
3. Worker continuously pops from the Redis queue
4. Worker upserts the vote into PostgreSQL (voter_id is unique — one vote per user)
5. User visits :5001 to see live results
6. Node.js queries PostgreSQL and renders the count — page auto-refreshes every 3s
```

---

## 🔧 Swarm Commands

```bash
# Scale the vote service to 4 replicas
docker service scale voting-app_vote=4

# Update worker image with zero-downtime rolling update
docker service update --image sharjikahamed/worker:v2 voting-app_worker

# View all running tasks
docker service ps voting-app_vote

# Remove the entire stack
docker stack rm voting-app

# Leave swarm (worker nodes)
docker swarm leave

# Leave swarm (manager — force)
docker swarm leave --force
```

---

## 🌐 Overlay Networks

Two isolated overlay networks are created by Docker Swarm:

| Network    | Connected Services           | Purpose                          |
|------------|------------------------------|----------------------------------|
| `frontend` | vote, result, redis, worker  | Vote submission and queue access |
| `backend`  | result, worker, db           | Database reads and writes        |

> **Note:** The `vote` service cannot directly reach `db` — it is isolated to the frontend network. Only the `worker` bridges both.

---

## 🩺 Health & Fault Tolerance

- **Vote service** has a built-in HTTP health check (`curl localhost:80`)
- **Worker** reconnects automatically if Redis or PostgreSQL drops
- **Swarm restart policies** bring failed containers back on-failure
- **PostgreSQL data** is persisted in a named volume (`db-data`) — votes survive restarts

---

## 🛠️ Customise the Options

Change the vote choices by setting environment variables in `docker-stack.yml`:

```yaml
environment:
  - OPTION_A=Pizza
  - OPTION_B=Burgers
```

Then redeploy: `docker stack deploy -c docker-stack.yml voting-app`

---

## 🧠 What I Learned Building This

- How **Docker Swarm overlay networks** isolate services while allowing controlled communication
- How **Redis** works as a lightweight message queue between producers and consumers
- How **Docker service replicas** enable load balancing across multiple containers — requests to `:5000` are distributed between both vote replicas automatically
- How **placement constraints** (`node.role == manager`) ensure stateful services like PostgreSQL run on predictable nodes
- How **upsert logic** (`ON CONFLICT DO UPDATE`) lets users change their vote without creating duplicates
- Why **worker retry loops** matter — in a distributed system, services start at different speeds and connections must be resilient

---

## 👤 Author

**S. Sharjik Ahamed**
Aspiring Cloud & DevOps Engineer — Chennai, India

[![GitHub](https://img.shields.io/badge/GitHub-Mdsarjik-181717?style=flat&logo=github)](https://github.com/Mdsarjik)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Sharjik_Ahamed-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/sharjik-ahamed-b66285335)
[![Docker Hub](https://img.shields.io/badge/DockerHub-sharjikahamed-2496ED?style=flat&logo=docker&logoColor=white)](https://hub.docker.com/u/sharjikahamed)

---

## 📄 License

MIT — free to use, fork, and learn from.
