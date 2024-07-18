#pragma once

#include "keys.h"

#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include "../settings.h"

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
inline int sync_client_fd = -1;
inline int sync_conn_fd = -1;
inline int sync_port = -1;

inline int syncServerInit() {
    int server_fd;
    // ssize_t valread;
    struct sockaddr_in address;
    // int opt = 1;
    socklen_t addrlen = sizeof(address);

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("[SyncServer] Socket creation failed");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(0); // let the OS choose an empty port

    // Bind the server's socket to a port
    if (bind(server_fd, (struct sockaddr*)&address,
             sizeof(address))
        < 0) {
        perror("[SyncServer] Bind failed");
        exit(EXIT_FAILURE);
    }

    // Get the port that the server has connected to
    struct sockaddr_in servaddr;
    bzero(&servaddr, sizeof(servaddr));
    socklen_t len = sizeof(servaddr);
    getsockname(server_fd, (struct sockaddr *) &servaddr, &len);
    // Set the value of the global `sync_port` variable,
    // this is used in `syncClientInit` to know which port to connect to
    sync_port = ntohs(servaddr.sin_port);

    // Listen (blocking) for the client to connect
    if (listen(server_fd, 3) < 0) {
        perror("[SyncServer] Failed to listen");
        exit(EXIT_FAILURE);
    }

    // Accept client's connection
    if ((sync_conn_fd
         = accept(server_fd, (struct sockaddr*)&address, &addrlen)) < 0) {
        perror("[SyncServer] Connection accept error");
        exit(EXIT_FAILURE);
    }

    // printf("=> Sync Server connected @ %d\n", sync_port);
    return 0;
}

inline int syncClientInit() {
    int status;
    struct sockaddr_in serv_addr;
    if ((sync_client_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("[SycClient] Socket creation error");
        exit(EXIT_FAILURE);
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(sync_port);

    // Convert IPv4 and IPv6 addresses from text to binary
    // form
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)
        <= 0) {
        perror("[SycClient] Invalid address");
        exit(EXIT_FAILURE);
    }

    // Connect to the server @ sync_port
    if ((status
         = connect(sync_client_fd, (struct sockaddr*)&serv_addr,
                   sizeof(serv_addr)))
        < 0) {
        perror("[SycClient] Connection failed");
        exit(EXIT_FAILURE);
    }

    // printf("=> Sync Client connected @ %d\n", sync_port);
    return 0;
}

inline void syncServerStep() {
    if (sync_conn_fd == -1)
        syncServerInit();

    char msg[2];
    if (read(sync_conn_fd, msg, 2) <= 0) {
        perror("[syncServerStep] Step failed");
        exit(EXIT_FAILURE);
    }
}

inline void syncClientStep() {
    if (sync_client_fd == -1)
        syncClientInit();

    /* Send a dummy message of two bytes */
    if (send(sync_client_fd, "-", 2, 0) <= 0) {
        perror("[syncClientStep] Step failed");
        exit(EXIT_FAILURE);
    }
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
