#pragma once

#include "keys.h"

#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <mutex>

/*

  "Virtual" keyboard input handling
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*/
inline bool virtual_key_presses[KeyType::INTERNAL_ENUM_COUNT];
inline int virtual_mouse_x = 0;
inline int virtual_mouse_y = 0;


/*

  Synchronization between minetest's server and client
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*/
inline int sync_port = -1;
inline std::mutex sync_port_mtx;

inline int sync_client_fd = -1;
inline int sync_conn_fd = -1;

inline int getSyncPort() {
    int port;

    sync_port_mtx.lock();

    if (sync_port < 0) {
        // select a random port in the range [65535, 49152] (dynamic ports' range)
        sync_port = (rand() % (65535 - 49152 + 1)) + 49152;
        printf("*** Internal sync port set to %d\n", sync_port);
    }

    port = sync_port;

    sync_port_mtx.unlock();

    return port;
}

inline int syncServerInit() {
    int server_fd;
    // ssize_t valread;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);
    // char buffer[1024] = { 0 };
    // char* hello = "Hello from server";

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET,
                   SO_REUSEADDR | SO_REUSEPORT, &opt,
                   sizeof(opt))) {
        printf("[SyncServer] setsockopt failed\n");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(getSyncPort());

    // Forcefully attaching socket to the port
    if (bind(server_fd, (struct sockaddr*)&address,
             sizeof(address))
        < 0) {
        printf("[SyncServer] Bind failed\n");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, 3) < 0) {
        printf("[SyncServer] Failed to listen\n");
        exit(EXIT_FAILURE);
    }
    if ((sync_conn_fd
         = accept(server_fd, (struct sockaddr*)&address, &addrlen)) < 0) {
        printf("[SyncServer] Connection accept error\n");
        exit(EXIT_FAILURE);
    }

    // Set receive and send timeout on the socket
    struct timeval timeout;
    timeout.tv_sec = 2;  /* timeout time in seconds */
    timeout.tv_usec = 0;
    if (setsockopt(sync_conn_fd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout, sizeof(timeout)) < 0) {
        printf("[SyncServer] setsockopt failed\n");
        exit(EXIT_FAILURE);
    }
    if (setsockopt(sync_conn_fd, SOL_SOCKET, SO_SNDTIMEO, (const char*)&timeout, sizeof(timeout)) < 0) {
        printf("[SyncServer] setsockopt failed\n");
        exit(EXIT_FAILURE);
    }

    printf("=> Sync Server connected\n");

    return 0;
}

inline int syncClientInit() {
    int status;
    struct sockaddr_in serv_addr;
    if ((sync_client_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("[SycClient] Socket creation error\n");
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(getSyncPort());

    // Convert IPv4 and IPv6 addresses from text to binary
    // form
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)
        <= 0) {
        printf("[SycClient] Invalid address\n");
        return -1;
    }

    if ((status
         = connect(sync_client_fd, (struct sockaddr*)&serv_addr,
                   sizeof(serv_addr)))
        < 0) {
        printf("[SycClient] Connection Failed\n");
        return -1;
    }

    printf("=> Sync Client connected\n");
    return 0;
}

inline void syncServerStep() {
    if (sync_conn_fd == -1)
        syncServerInit();

    char msg[2];
    read(sync_conn_fd, msg, 2);
}

inline void syncClientStep() {
    if (sync_client_fd == -1)
        syncClientInit();

    /* Send a dummy message of two bytes */
    send(sync_client_fd, "-", 2, 0);
}

/*

  Reward and termination signal system
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*/
inline double g_reward = 0.0; /* Global variable of the reward value */

/* Values used by `lua_set_reward_once`: */
inline bool g_reward_reset = false;  /* Whether to reset the reward value after one iteration */
inline double g_reward_reset_value = 0.0; /* The value to reset the reward to */

inline bool g_termination = false; /* Global variable with the termination flag */

extern "C" {
#include <lualib.h>
}

/* Implementation of the Lua functions to get/set the global reward value */
inline static int lua_set_reward(lua_State *L) {
    double d = lua_tonumber(L, 1);  /* get argument */
    g_reward = d;
    return 0; /* number of results */
}

inline static int lua_set_reward_once(lua_State *L) {
    /* get the two arguments */
    double val = lua_tonumber(L, 1);
    double reset_val = lua_tonumber(L, 2);

    g_reward = val;
    g_reward_reset_value = reset_val;
    g_reward_reset = true;

    return 0; /* number of results */
}

inline static int lua_get_reward(lua_State *L) {
    lua_pushnumber(L, g_reward);
    return 1; /* number of results */
}

/* Implementation of the Lua functions to get/set the global termination flag */
inline static int lua_set_termination(lua_State *L) {
    g_termination = true;
    return 0; /* number of results */
}

inline static int lua_get_termination(lua_State *L) {
    lua_pushnumber(L, (int)g_termination);
    return 1; /* number of results */
}
