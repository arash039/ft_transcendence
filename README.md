# Pong Game Remote Player and DevOps Modules

## Overview
Pong 3.0 game consists of two main parts: users without registering can play the game either againts another user, or against an AI opponent on the "same machine", and if they register they can log in and play against remote players. Remote play has three main features: two players mode, four players mode, and an online tournament where 4 players can play two by two in a tournamnet to see who will be the champion.

This README mainly focuses on two main aspects of the Pong 3.0 project. First the [Remote Player Game](#remote-player-game) is discussed and then in the [DevOps](#devops) section it demonstrates how ELK stack is used for log management, and Prometheus and Grafana are integrated to provide robust monitoring and performance visualization.

### Remote Player Game

#### 1. The Game Flow: Connecting, Playing, and Updating State

At the core of this project is the `PongConsumer` class, which manages all WebSocket interactions and game logic. When a player connects, the consumer establishes a WebSocket connection and verifies whether they are reconnecting to an existing session or joining a new one. The consumer then assigns the player to an active game session or creates a new session if needed.

Upon establishing a connection, players can start moving their paddles. The game continuously sends and receives data to and from each player to maintain synchronization. Paddle positions, ball movements, and scores are all tracked in real-time. The backend continuously calculates these updates, considering player actions and collision events, before broadcasting the updated state to all connected players.
#### 2. Real-Time Synchronization and Game Management

The game state is maintained through various data structures. A dictionary called game_sessions tracks ongoing sessions, storing each session’s player details, game state (e.g., ball and paddle positions, scores), and the ongoing game loop task. The game loop runs at a specified frames-per-second (FPS) rate, ensuring the game logic, including ball movement and collision detection, is executed smoothly.

If a player disconnects, the consumer registers the disconnection and marks a timeout for possible reconnection. The disconnected_players dictionary and the rejoin_timeout variable work together to manage the player’s re-entry window. Should a player return within the allowed time, they can seamlessly rejoin the game where they left off.
#### 3. Handling Game Events: Starting, Pausing, and Ending Games

From the moment both players are ready, the game initiates a countdown using the `start_game_countdown()` method. Once the countdown completes, the game loop begins. This loop is the heart of the game, handling ball movement calculations, paddle interactions, and collisions. The game progresses until a player reaches the winning score, at which point the game declares the winner and terminates the session.

Additionally, various event-based messages are broadcasted to the clients, such as when both players join, when one player rejoins after a disconnection, and when the game concludes. The backend is designed to notify users of these key events using the respective methods like `player_joined()`, `game_started()`, and `game_over()`.
#### 4. Transitioning to Tournaments: Managing Multiple Games

While the individual Pong game sessions are engaging on their own, the project extends this by offering a tournament mode. Here, players can join and compete in a bracketed tournament, with matches progressing until a champion is crowned.

The tournament-specific consumer, `TournamentConsumer`, coordinates the entire process. Upon connecting, players are added to the tournament bracket, and WebSocket communication ensures the tournament chart is constantly updated for all participants. When a match begins, players are directed to their game session, where the same core game logic is applied. As matches conclude, the tournament consumer updates the standings and prepares the next round.
#### 5. Frontend-Backend Coordination: A Smooth User Experience

The frontend, built primarily with JavaScript, plays a crucial role in managing user interactions and rendering game visuals. The game UI is rendered dynamically, responding to game state updates received over WebSocket. Functions like `startGame(sessionId, oldSocket)` in tour_game.js manage the initialization of the WebSocket connection, while handlers like `updateGameState(state)` ensure the visuals stay in sync with the backend.

In the tournament setup (tour.js), the frontend coordinates actions like starting the tournament and navigating between matches. It listens for updates and user actions, pushing commands back to the backend for processing, whether it’s updating the tournament chart or navigating players to their next match.
#### 6. Error Handling and Robustness

The system is designed to handle common issues like network disruptions, errors during state updates, and unexpected disconnections. The consumer logs these events, ensuring the system can respond gracefully. For instance, if a player disconnects mid-game, the consumer tracks the disconnection and offers a reconnection window. The backend ensures that state errors don’t crash the game loop, allowing the match to continue seamlessly.

## DevOps

The project also integrates the ELK stack (Elasticsearch, Logstash, and Kibana) for centralized logging and real-time log analysis. The ELK setup collects and aggregates logs from the Django Channels backend, providing powerful search and filtering capabilities for debugging and monitoring. Logstasg integrates seamlessly with Elasticsearch and Kibana which offers intuitive visualizations and dashboards, making it easier to track game sessions, player activity, and system events.

Prometheus and Grafana are integrated to provide robust monitoring and performance visualization for the project. Prometheus collects metrics like game session durations, WebSocket connection performance, and system resource usage. Grafana visualizes these metrics through customizable dashboards, enabling real-time insights into application health and behavior. This setup helps ensure smooth performance and early detection of any potential issues during gameplay and tournament management.

Upon running the docker compose, docker images for each service is created and necessary pre-made configuration files are copied into the containers. Each service has a run script that sets up the container and ensures its performance.

A `.env` file is needed to provide the containers with necessary credentials and settings.

### Files

#### ELK:

- `logstash.conf`: Defines the input, filter, and output stages of the data pipeline, allowing you to customize how data is processed before being sent to Elasticsearch.

- `ilm-policy.json`: Defines how indices are managed throughout their lifecycle, including transitions between hot, warm, and delete phases.

- `index-template.json`: Establishes index patterns, mappings, and settings that are automatically applied when a new index is created.

- `dashboard_provisioning.yml`: Provisions the dashboards automatically in Grafana. This file allows you to preconfigure dashboards by defining them as code, which can be especially useful when deploying Grafana in automated environments, like Docker.

#### Prometheus and Grafana:

- `alert_rules.yml`: This configuration is used to define alert rules in Prometheus, specifying under what conditions an alert should be triggered and how it should be labeled and annotated.

- `prometheus.yml`: Prometheus configuration file that defines settings related to global settings, scrape configurations, alerting, and rule files. 

- `datasources.yml`: This configuration would typically be used in scenarios where Grafana is deployed alongside Prometheus (e.g., in a Docker or Kubernetes environment) and you want to automate the setup of the Prometheus datasource when Grafana starts.

