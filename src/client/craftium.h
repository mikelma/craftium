#pragma once

#include "keys.h"

#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <semaphore.h>
#include <fcntl.h>

#include <cstdint>

#include "../settings.h"


inline char actions[27];

/*

  Frameskip
  ~~~~~~~~~

*/
inline int frameskip_count = 0;
// The value of this variable is set in the Client::startPyConn
// method according to the frameskip setting
inline int frameskip = 0;

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

inline char *srv_sem_name_A;
inline char *srv_sem_name_B;
inline sem_t *srv_sem_A = nullptr;
inline sem_t *srv_sem_B = nullptr;

inline char *cli_sem_name_A;
inline char *cli_sem_name_B;
inline sem_t *cli_sem_A = nullptr;
inline sem_t *cli_sem_B = nullptr;

inline int syncServerInit()
{
    // Create the name of the semaphore based on the port number that commicates MT server and client
    srv_sem_name_A = (char*)malloc(20 * sizeof(char));
    srv_sem_name_B = (char*)malloc(20 * sizeof(char));
    sprintf(srv_sem_name_A, "/crftA%d", g_settings->getU16("port"));
    sprintf(srv_sem_name_B, "/crftB%d", g_settings->getU16("port"));

    /*
    printf("Creating semaphore with name '%s'\n", srv_sem_name_A);
    printf("Creating semaphore with name '%s'\n", srv_sem_name_B);
    */

    // Create the sempaphores with an initial value of 1
    if ((srv_sem_A = sem_open(srv_sem_name_A, O_CREAT, 0644, 0)) == SEM_FAILED) {
        perror("[SyncServer] Failed to create semaphore A");
        exit(EXIT_FAILURE);
    }

    if ((srv_sem_B = sem_open(srv_sem_name_B, O_CREAT, 0644, 0)) == SEM_FAILED) {
        perror("[SyncServer] Failed to create semaphore B");
        exit(EXIT_FAILURE);
    }

    return 0;
}

inline int syncClientInit() {
    cli_sem_name_A = (char*)malloc(20 * sizeof(char));
    cli_sem_name_B = (char*)malloc(20 * sizeof(char));
    sprintf(cli_sem_name_A, "/crftA%d", g_settings->getU16("port"));
    sprintf(cli_sem_name_B, "/crftB%d", g_settings->getU16("port"));

    /*
    printf("Creating semaphore with name '%s'\n", cli_sem_name_A);
    printf("Creating semaphore with name '%s'\n", cli_sem_name_B);
    */

    if ((cli_sem_A = sem_open(cli_sem_name_A, 0)) == SEM_FAILED) {
        perror("[SyncClient] Failed  to open semaphore A");
        exit(EXIT_FAILURE);
    }

    if ((cli_sem_B = sem_open(cli_sem_name_B, 0)) == SEM_FAILED) {
        perror("[SyncClient] Failed  to open semaphore B");
        exit(EXIT_FAILURE);
    }

    return 0;
}

inline void syncServerStep() {
    if (!g_settings->getBool("sync_env_mode")) {
        return;
    }

    // printf("<= SRV start\n");

    if (srv_sem_A == nullptr)
        syncServerInit();


    if (sem_post(srv_sem_B) < 0) {
        perror("[SyncServerStep] Error posting sem B");
        exit(EXIT_FAILURE);
    }

    if (sem_wait(srv_sem_A) < 0) {
        perror("[SyncServerStep] Error waiting sem A");
        exit(EXIT_FAILURE);
    }

    // printf("=> SRV end\n");
}

inline void syncClientStep() {
    if (!g_settings->getBool("sync_env_mode")) {
        return;
    }
    // printf("> CLI start\n");

    if (cli_sem_A == nullptr)
      syncClientInit();

    if (sem_post(cli_sem_A) < 0) {
        perror("[SyncServerStep] Error posting sem A");
        exit(EXIT_FAILURE);
    }

    if (sem_wait(cli_sem_B) < 0) {
        perror("[SyncServerStep] Error waiting sem B");
        exit(EXIT_FAILURE);
    }

    // printf("< CLI end\n");
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
inline bool g_soft_reset = false; /* Global variable with the termination flag */

inline std::vector<uint32_t> g_voxel_data = std::vector<uint32_t>(1,0);
inline std::vector<uint32_t> g_voxel_light_data = std::vector<uint32_t>(1,0);
inline std::vector<uint32_t> g_voxel_param2_data = std::vector<uint32_t>(1,0);

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

inline static int lua_reset_termination(lua_State *L) {
    g_termination = false;
    g_soft_reset = false;
    return 0; /* number of results */
}

inline static int lua_get_termination(lua_State *L) {
    lua_pushnumber(L, (int)g_termination);
    return 1; /* number of results */
}

inline static int lua_get_soft_reset(lua_State *L) {
    lua_pushnumber(L, (int)g_soft_reset);
    return 1; /* number of results */
}

inline static std::vector<uint32_t> lua_set_array_uint32_t(lua_State* L) {

    // Get the returned table
    std::vector<uint32_t> result;

    if (!lua_istable(L, -1)) {
        throw std::runtime_error("Expected table return when calling lua_set_array_uint32_t");
    }

    // Iterate through the table
    lua_pushnil(L);  // First key
    while (lua_next(L, -2) != 0) {
        // Value is at -1, key at -2
        result.push_back(lua_tointeger(L, -1));
        lua_pop(L, 1);  // Remove value, keep key for next iteration
    }

    // Clean up the stack
    lua_pop(L, 1);
    return result;
}

inline static int lua_set_voxel_data(lua_State* L) {
	g_voxel_data = lua_set_array_uint32_t(L);
	return 0;
}

inline static int lua_set_voxel_light_data(lua_State* L) {
	g_voxel_light_data = lua_set_array_uint32_t(L);
	return 0;
}

inline static int lua_set_voxel_param2_data(lua_State* L) {
	g_voxel_param2_data = lua_set_array_uint32_t(L);
	return 0;
}
