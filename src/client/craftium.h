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

#include "../settings.h"


#include <string>
#include <unordered_map>
#include <variant>


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

using Value = std::variant<bool, int, float, double, std::string>;
using List = std::vector<Value>;
using Dict = std::unordered_map<std::string, Value>;
using InfoMap = std::unordered_map<std::string, std::variant<List, Dict, bool, int, float, double, std::string>>;

inline InfoMap g_info;  /* Global variable with the information dictionary */

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

inline static int lua_set_info(lua_State *L) {

    const char *key = lua_tostring(L, 1);
    if (!key){
        return 0;
    }
    if (lua_type(L,2) == LUA_TBOOLEAN){
        bool val = lua_toboolean(L, 2);
        g_info[key] = val;
        return 0; /* number of results */
    } else if (lua_type(L, 2) == LUA_TNUMBER) {
        lua_Number num = lua_tonumber(L, 2); 
        if (static_cast<lua_Integer>(num) == num) {
            g_info[key] = static_cast<int>(num);
        } else if (static_cast<float>(num) == num) {
            g_info[key] = static_cast<float>(num);
        } else {
            g_info[key] = static_cast<double>(num);
        }
        return 0; /* number of results */
    } else if (lua_type(L, 2) == LUA_TSTRING) {
        std::string val = lua_tostring(L, 2);
        g_info[key] = val;
        return 0; /* number of results */
    } else {
        return 0;
    }
}


inline static int lua_reset_info(lua_State *L) {
    g_info.clear();
    return 0; /* number of results */
}


inline static int lua_get_from_info(lua_State *L) {

    const char *key = lua_tostring(L,1);
    if (!key) {
        lua_pushnil(L);
        return 1;
    }

    auto iter = g_info.find(key);
    if (iter == g_info.end()){
        lua_pushnil(L);
        return 1;
    }

    if (std::holds_alternative<List>(iter->second) || std::holds_alternative<Dict>(iter->second)){
        lua_pushnil(L);
        return 1;
    }



    if (std::holds_alternative<bool>(iter->second)){
        lua_pushboolean(L, std::get<bool>(iter->second));
    } else if (std::holds_alternative<int>(iter->second)) {
        lua_pushinteger(L,std::get<int>(iter->second));
    } else if (std::holds_alternative<float>(iter->second)) {
        lua_pushnumber(L,std::get<float>(iter->second));
    } else if (std::holds_alternative<double>(iter->second)) {
        lua_pushnumber(L, std::get<double>(iter->second));
    } else if (std::holds_alternative<std::string>(iter->second)) {
        lua_pushstring(L,std::get<std::string>(iter->second).c_str());
    } else {
        lua_pushnil(L);
    }

    return 1; /* number of results */
}


inline static int lua_remove_from_info(lua_State *L){
    
    auto iter = g_info.find(lua_tostring(L, 1));

    // Delete the pair with key if found
    if (iter != g_info.end()) {
        g_info.erase(iter);
    }

    return 0; /* number of results */
}

inline static int lua_info_contains(lua_State *L){
    
    auto iter = g_info.find(lua_tostring(L, 1));

    lua_pushboolean(L, iter != g_info.end());

    return 1; /* number of results */
}

inline static int lua_set_empty_list(lua_State *L){
    const char *key = lua_tostring(L, 1);
    if (!key){
        return 0;
    }
    
    g_info[key] = List();
    return 0; /* number of results */

}

inline static int lua_add_to_list(lua_State *L){
    const char *key = lua_tostring(L, 1);
    if (!key){
        return 0;
    }
    
    Value val;

    if (lua_type(L,2) == LUA_TBOOLEAN){
        val = lua_toboolean(L, 2);
    } else if (lua_type(L, 2) == LUA_TNUMBER) {
        lua_Number num = lua_tonumber(L, 2); 
        if (static_cast<lua_Integer>(num) == num) {
            val = static_cast<int>(num);
        } else if (static_cast<float>(num) == num) {
            val = static_cast<float>(num);
        } else {
            val = static_cast<double>(num);
        }
    } else if (lua_type(L, 2) == LUA_TSTRING) {
        val = lua_tostring(L, 2);
    } else {
        return 0;
    }

    auto iter = g_info.find(key);
    if (iter == g_info.end()){
        g_info[key] = List{val};
        return 0;
    } else if (!std::holds_alternative<List>(iter->second)){
        return 0;
    }

    std::get<List>(iter->second).push_back(val);

    return 0;

}

inline static int lua_set_empty_dict(lua_State *L){
    const char *key = lua_tostring(L, 1);
    if (!key){
        return 0;
    }
    
    g_info[key] = Dict();
    return 0; /* number of results */

}

inline static int lua_add_to_dict(lua_State *L){
    const char *key = lua_tostring(L, 1);
    if (!key){
        return 0;
    }

    const char *key2 = lua_tostring(L, 2);
    if (!key2){
        return 0;
    }
    
    Value val;

    if (lua_type(L,3) == LUA_TBOOLEAN){
        val = (bool)lua_toboolean(L, 3);
    } else if (lua_type(L, 3) == LUA_TNUMBER) {
        lua_Number num = lua_tonumber(L, 3); 
        if (static_cast<lua_Integer>(num) == num) {
            val = static_cast<int>(num);
        } else if (static_cast<float>(num) == num) {
            val = static_cast<float>(num);
        } else {
            val = static_cast<double>(num);
        }
    } else if (lua_type(L, 3) == LUA_TSTRING) {
        val = lua_tostring(L, 3);
    } else {
        return 0;
    }

    auto iter = g_info.find(key);
    if (iter == g_info.end()){
        g_info[key] = Dict{{key2, val}};
        return 0;
    } else if (!std::holds_alternative<Dict>(iter->second)){
        return 0;
    }

    std::get<Dict>(iter->second)[key2]=val;

    return 0;

}

inline static int lua_dict_contains(lua_State *L){
    const char *key = lua_tostring(L, 1);
    if (!key){
        lua_pushnil(L);
        return 1;
    }

    const char *key2 = lua_tostring(L, 2);
    if (!key2){
        lua_pushnil(L);
        return 1;
    }

    auto iter = g_info.find(key);
    if (iter == g_info.end()){
        lua_pushnil(L);
        return 1;
    }

    if (!std::holds_alternative<Dict>(iter->second)){
        lua_pushnil(L);
        return 1;
    }

    auto iter2 = std::get<Dict>(iter->second).find(key2);

    lua_pushboolean(L, iter2 != std::get<Dict>(iter->second).end());

    return 1; /* number of results */
}

inline static int lua_get_from_dict(lua_State *L) {

    const char *key = lua_tostring(L,1);
    if (!key) {
        lua_pushnil(L);
        return 1;
    }

    const char *key2 = lua_tostring(L,2);
    if (!key2) {
        lua_pushnil(L);
        return 1;
    }

    auto iter = g_info.find(key);
    if (iter == g_info.end()){
        lua_pushnil(L);
        return 1;
    }

    if (!std::holds_alternative<Dict>(iter->second)){
        lua_pushnil(L);
        return 1;
    }

    auto iter2 = std::get<Dict>(iter->second).find(key2);
    if (iter2 == std::get<Dict>(iter->second).end()){
        lua_pushnil(L);
        return 1;
    }

    if (std::holds_alternative<bool>(iter2->second)){
        lua_pushboolean(L, std::get<bool>(iter2->second));
    } else if (std::holds_alternative<int>(iter2->second)) {
        lua_pushinteger(L,std::get<int>(iter2->second));
    } else if (std::holds_alternative<float>(iter2->second)) {
        lua_pushnumber(L,std::get<float>(iter2->second));
    } else if (std::holds_alternative<double>(iter2->second)) {
        lua_pushnumber(L, std::get<double>(iter2->second));
    } else if (std::holds_alternative<std::string>(iter2->second)) {
        lua_pushstring(L,std::get<std::string>(iter2->second).c_str());
    } else {
        lua_pushnil(L);
    }

    return 1; /* number of results */
}
